#!/usr/bin/env python3
"""
Complete Music Production Automation Workflow Example

Demonstrates the full workflow from slicing samples from recordings
to arranging compositions, ready for Ableton Live integration.

This example shows:
1. Loading audio file
2. Detecting onsets (for slicing)
3. Detecting beats/tempo (for quantization)
4. Detecting chords/key (for harmonic arrangement)
5. Detecting downbeats (for measure alignment)
6. Exporting results for Ableton Live integration
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from madmom.audio import SignalProcessor
from madmom.features import (
    CNNKeyRecognitionProcessor,
    CRFChordRecognitionProcessor,
    DBNBeatTrackingProcessor,
    DBNDownBeatTrackingProcessor,
    OnsetPeakPickingProcessor,
    RNNBeatProcessor,
    RNNDownBeatProcessor,
    RNNOnsetProcessor,
    TempoEstimationProcessor,
)
from madmom.io import write_beats, write_chords, write_key, write_onsets


def analyze_audio_file(audio_file: Path | str) -> dict[str, Any]:
    """
    Perform comprehensive audio analysis for music production automation.
    
    Args:
        audio_file: Path to audio file to analyze
        
    Returns:
        Dictionary containing all analysis results
    """
    audio_path = Path(audio_file)
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    print(f"Loading audio: {audio_path}")
    audio = SignalProcessor()(str(audio_path))
    
    results = {
        "audio_file": str(audio_path),
        "onsets": None,
        "beats": None,
        "tempo": None,
        "chords": None,
        "key": None,
        "downbeats": None,
    }
    
    # 1. Detect onsets for sample slicing
    print("Detecting onsets for sample slicing...")
    onset_processor = RNNOnsetProcessor()
    onset_activations = onset_processor(audio)
    peak_picker = OnsetPeakPickingProcessor()
    onsets = peak_picker(onset_activations)
    results["onsets"] = onsets.tolist()
    print(f"  ✓ Detected {len(onsets)} onsets")
    
    # 2. Detect beats and tempo for quantization
    print("Detecting beats and tempo...")
    beat_processor = RNNBeatProcessor()
    beat_activations = beat_processor(audio)
    
    tempo_processor = TempoEstimationProcessor()
    tempi = tempo_processor(beat_activations)
    primary_tempo = float(tempi[0][0])
    primary_strength = float(tempi[0][1])
    results["tempo"] = {
        "primary": primary_tempo,
        "strength": primary_strength,
        "candidates": [[float(t[0]), float(t[1])] for t in tempi],
    }
    print(f"  ✓ Detected tempo: {primary_tempo:.2f} BPM (strength: {primary_strength:.2f})")
    
    beat_tracker = DBNBeatTrackingProcessor()
    beats = beat_tracker(beat_activations)
    results["beats"] = beats.tolist()
    print(f"  ✓ Detected {len(beats)} beats")
    
    # 3. Detect chords and key for harmonic arrangement
    print("Detecting chords and key...")
    chord_processor = CRFChordRecognitionProcessor()
    chords = chord_processor(audio)
    results["chords"] = [
        {"start": float(c["start"]), "end": float(c["end"]), "chord": str(c["label"])}
        for c in chords
    ]
    print(f"  ✓ Detected {len(chords)} chord segments")
    
    key_processor = CNNKeyRecognitionProcessor()
    key = str(key_processor(audio))
    results["key"] = key
    print(f"  ✓ Detected key: {key}")
    
    # 4. Detect downbeats for measure alignment (Ableton Live integration)
    print("Detecting downbeats for measure alignment...")
    downbeat_processor = RNNDownBeatProcessor()
    downbeat_activations = downbeat_processor(audio)
    downbeat_tracker = DBNDownBeatTrackingProcessor()
    beats_downbeats = downbeat_tracker(downbeat_activations)
    
    # Separate beats and downbeats
    all_beats = beats_downbeats[:, 0]
    downbeats = beats_downbeats[beats_downbeats[:, 1] == 1][:, 0]
    results["downbeats"] = downbeats.tolist()
    print(f"  ✓ Detected {len(downbeats)} downbeats (measure boundaries)")
    
    return results


def export_for_ableton(results: dict[str, Any], output_dir: Path) -> None:
    """
    Export analysis results in formats suitable for Ableton Live integration.
    
    Args:
        results: Analysis results dictionary
        output_dir: Directory to save exported files
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    base_name = Path(results["audio_file"]).stem
    
    # Export individual analysis files
    if results["beats"]:
        beats_file = output_dir / f"{base_name}_beats.txt"
        write_beats(np.array(results["beats"]), str(beats_file))
        print(f"  ✓ Exported beats to {beats_file}")
    
    if results["downbeats"]:
        downbeats_file = output_dir / f"{base_name}_downbeats.txt"
        write_beats(np.array(results["downbeats"]), str(downbeats_file))
        print(f"  ✓ Exported downbeats to {downbeats_file}")
    
    if results["onsets"]:
        onsets_file = output_dir / f"{base_name}_onsets.txt"
        write_onsets(np.array(results["onsets"]), str(onsets_file))
        print(f"  ✓ Exported onsets to {onsets_file}")
    
    if results["chords"]:
        chords_file = output_dir / f"{base_name}_chords.txt"
        write_chords(results["chords"], str(chords_file))
        print(f"  ✓ Exported chords to {chords_file}")
    
    if results["key"]:
        key_file = output_dir / f"{base_name}_key.txt"
        write_key(results["key"], str(key_file))
        print(f"  ✓ Exported key to {key_file}")
    
    # Export comprehensive JSON for programmatic use
    json_file = output_dir / f"{base_name}_analysis.json"
    with open(json_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"  ✓ Exported complete analysis to {json_file}")


def create_slicing_plan(results: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Create a slicing plan based on detected onsets and beats.
    
    Args:
        results: Analysis results dictionary
        
    Returns:
        List of slice definitions with timing and quantization info
    """
    onsets = np.array(results["onsets"])
    beats = np.array(results["beats"])
    tempo = results["tempo"]["primary"]
    
    slices = []
    for i, onset_time in enumerate(onsets):
        # Find nearest beat for quantization
        nearest_beat_idx = np.argmin(np.abs(beats - onset_time))
        nearest_beat = beats[nearest_beat_idx]
        quantization_offset = onset_time - nearest_beat
        
        # Calculate slice duration (to next onset or end of audio)
        if i < len(onsets) - 1:
            duration = onsets[i + 1] - onset_time
        else:
            # Last slice: use average duration or remaining time
            if len(onsets) > 1:
                avg_duration = np.mean(np.diff(onsets))
                duration = avg_duration
            else:
                duration = 1.0  # Default 1 second
        
        slices.append({
            "slice_id": i + 1,
            "start_time": float(onset_time),
            "duration": float(duration),
            "nearest_beat": float(nearest_beat),
            "quantization_offset": float(quantization_offset),
            "quantized_start": float(nearest_beat),  # Quantized to nearest beat
        })
    
    return slices


def create_arrangement_suggestion(results: dict[str, Any], slices: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Create arrangement suggestions based on harmonic analysis.
    
    Args:
        results: Analysis results dictionary
        slices: List of slice definitions
        
    Returns:
        Arrangement suggestion with harmonic grouping
    """
    key = results["key"]
    chords = results["chords"]
    downbeats = np.array(results["downbeats"])
    
    # Group slices by harmonic compatibility
    # (simplified: group by proximity to chord changes)
    arrangement = {
        "key": key,
        "tempo": results["tempo"]["primary"],
        "measures": [],
        "harmonic_sections": [],
    }
    
    # Create measure-based structure
    if len(downbeats) > 0:
        for i in range(len(downbeats) - 1):
            measure_start = downbeats[i]
            measure_end = downbeats[i + 1] if i + 1 < len(downbeats) else measure_start + 4.0  # Assume 4/4
            
            # Find chords in this measure
            measure_chords = [
                c for c in chords
                if measure_start <= c["start"] < measure_end
            ]
            
            # Find slices in this measure
            measure_slices = [
                s for s in slices
                if measure_start <= s["start_time"] < measure_end
            ]
            
            arrangement["measures"].append({
                "measure": i + 1,
                "start": float(measure_start),
                "end": float(measure_end),
                "chords": measure_chords,
                "slices": measure_slices,
            })
    
    return arrangement


def main():
    """Main workflow demonstration."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Complete music production automation workflow"
    )
    parser.add_argument("audio_file", type=str, help="Path to audio file")
    parser.add_argument(
        "-o", "--output-dir", type=str, default="output",
        help="Output directory for analysis results (default: output)"
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Export comprehensive JSON analysis"
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("Music Production Automation Workflow")
    print("=" * 70)
    print()
    
    # Perform comprehensive analysis
    results = analyze_audio_file(args.audio_file)
    
    print()
    print("Creating slicing plan...")
    slices = create_slicing_plan(results)
    print(f"  ✓ Created {len(slices)} slice definitions")
    
    print()
    print("Creating arrangement suggestions...")
    arrangement = create_arrangement_suggestion(results, slices)
    print(f"  ✓ Created arrangement with {len(arrangement['measures'])} measures")
    
    print()
    print("Exporting results...")
    export_for_ableton(results, args.output_dir)
    
    if args.json:
        output_dir = Path(args.output_dir)
        base_name = Path(args.audio_file).stem
        
        # Export slicing plan
        slicing_file = output_dir / f"{base_name}_slicing_plan.json"
        with open(slicing_file, "w") as f:
            json.dump(slices, f, indent=2)
        print(f"  ✓ Exported slicing plan to {slicing_file}")
        
        # Export arrangement suggestion
        arrangement_file = output_dir / f"{base_name}_arrangement.json"
        with open(arrangement_file, "w") as f:
            json.dump(arrangement, f, indent=2)
        print(f"  ✓ Exported arrangement to {arrangement_file}")
    
    print()
    print("=" * 70)
    print("Analysis complete!")
    print("=" * 70)
    print()
    print("Summary:")
    print(f"  - Audio file: {results['audio_file']}")
    print(f"  - Tempo: {results['tempo']['primary']:.2f} BPM")
    print(f"  - Key: {results['key']}")
    print(f"  - Beats: {len(results['beats'])}")
    print(f"  - Downbeats: {len(results['downbeats'])}")
    print(f"  - Onsets: {len(results['onsets'])} (for slicing)")
    print(f"  - Chords: {len(results['chords'])} segments")
    print(f"  - Slices: {len(slices)}")
    print()
    print(f"Results exported to: {args.output_dir}/")
    print()
    print("Next steps for Ableton Live integration:")
    print("  1. Import audio file into Ableton")
    print("  2. Use onsets to slice audio into samples")
    print("  3. Quantize slices to detected beats")
    print("  4. Arrange slices based on harmonic analysis (chords/key)")
    print("  5. Align to measures using downbeat information")


if __name__ == "__main__":
    main()

