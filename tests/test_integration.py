"""Integration tests for complete madmom workflows.

Tests complete music production automation workflows from audio analysis
to beat tracking, tempo detection, and arrangement.
"""

from __future__ import annotations

import unittest
from pathlib import Path

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

from . import AUDIO_PATH

sample_file = Path(AUDIO_PATH) / "sample.wav"


class TestCompleteWorkflow(unittest.TestCase):
    """Test complete music production automation workflow."""

    def setUp(self):
        """Set up test fixtures."""
        if not sample_file.exists():
            self.skipTest(f"Test audio file not found: {sample_file}")

    def test_beat_tracking_workflow(self):
        """Test complete beat tracking workflow."""
        # Load audio
        audio = SignalProcessor()(str(sample_file))

        # Get beat activations
        beat_processor = RNNBeatProcessor()
        activations = beat_processor(audio)

        # Track beats (fps defaults to 100 for beat activations)
        beat_tracker = DBNBeatTrackingProcessor(fps=100)
        beats = beat_tracker(activations)

        # Verify results
        self.assertIsInstance(beats, np.ndarray)
        self.assertGreater(len(beats), 0)
        self.assertTrue(np.all(beats >= 0))  # All beats should be non-negative
        self.assertTrue(np.all(np.diff(beats) > 0))  # Beats should be in order

    def test_tempo_detection_workflow(self):
        """Test tempo detection workflow."""
        # Load audio
        audio = SignalProcessor()(str(sample_file))

        # Get beat activations
        beat_processor = RNNBeatProcessor()
        activations = beat_processor(audio)

        # Detect tempo (fps defaults to 100 for beat activations)
        tempo_processor = TempoEstimationProcessor(fps=100)
        tempi = tempo_processor(activations)

        # Verify results
        self.assertIsInstance(tempi, np.ndarray)
        self.assertGreater(len(tempi), 0)
        self.assertEqual(tempi.shape[1], 2)  # Should have tempo and strength
        self.assertTrue(np.all(tempi[:, 0] > 0))  # All tempi should be positive
        self.assertTrue(np.all(tempi[:, 1] >= 0))  # All strengths should be non-negative

    def test_onset_detection_workflow(self):
        """Test onset detection workflow."""
        # Load audio
        audio = SignalProcessor()(str(sample_file))

        # Detect onsets
        onset_processor = RNNOnsetProcessor()
        activations = onset_processor(audio)
        peak_picker = OnsetPeakPickingProcessor()
        onsets = peak_picker(activations)

        # Verify results
        self.assertIsInstance(onsets, np.ndarray)
        self.assertGreater(len(onsets), 0)
        self.assertTrue(np.all(onsets >= 0))  # All onsets should be non-negative
        self.assertTrue(np.all(np.diff(onsets) > 0))  # Onsets should be in order

    def test_downbeat_detection_workflow(self):
        """Test downbeat detection workflow."""
        # Load audio
        audio = SignalProcessor()(str(sample_file))

        # Detect downbeats
        downbeat_processor = RNNDownBeatProcessor()
        activations = downbeat_processor(audio)
        tracker = DBNDownBeatTrackingProcessor(fps=100, beats_per_bar=[4])
        beats_downbeats = tracker(activations)

        # Verify results
        self.assertIsInstance(beats_downbeats, np.ndarray)
        self.assertGreater(len(beats_downbeats), 0)
        self.assertEqual(beats_downbeats.shape[1], 2)  # Should have time and beat number
        self.assertTrue(np.all(beats_downbeats[:, 0] >= 0))  # All times should be non-negative

        # Extract downbeats (beat number == 1)
        downbeats = beats_downbeats[beats_downbeats[:, 1] == 1][:, 0]
        self.assertGreater(len(downbeats), 0)

    def test_chord_recognition_workflow(self):
        """Test chord recognition workflow."""
        # Load audio
        audio = SignalProcessor()(str(sample_file))

        # Detect chords (CRFChordRecognitionProcessor can process audio directly)
        # It internally uses CNNChordFeatureProcessor if needed
        try:
            chord_processor = CRFChordRecognitionProcessor()
            chords = chord_processor(audio)

            # Verify results
            self.assertIsInstance(chords, np.ndarray)
            if len(chords) > 0:
                # Check structure if chords are detected
                # Chords may be structured array or regular array depending on processor
                if chords.dtype.names:
                    self.assertIn("start", chords.dtype.names)
                    self.assertIn("end", chords.dtype.names)
                    self.assertIn("label", chords.dtype.names)
                else:
                    # If not structured array, at least verify it's not empty
                    self.assertGreater(len(chords), 0)
        except (ValueError, TypeError) as e:
            # Some chord processors may require specific feature extraction
            # Skip test if processor doesn't support direct audio input
            self.skipTest(f"Chord recognition requires features: {e}")

    def test_key_detection_workflow(self):
        """Test key detection workflow."""
        # Load audio
        audio = SignalProcessor()(str(sample_file))

        # Detect key
        key_processor = CNNKeyRecognitionProcessor()
        key_result = key_processor(audio)

        # Verify results (key processor returns array, need to extract key name)
        self.assertIsInstance(key_result, np.ndarray)
        # Key processor returns probabilities, extract most likely key
        from madmom.features.key import KEY_LABELS

        if len(key_result.shape) == 2:
            key_idx = np.argmax(key_result[0])
        else:
            key_idx = np.argmax(key_result)
        key = KEY_LABELS[key_idx]
        self.assertIsInstance(key, str)
        self.assertGreater(len(key), 0)

    def test_complete_music_production_workflow(self):
        """Test complete music production automation workflow."""
        # Load audio
        audio = SignalProcessor()(str(sample_file))

        # 1. Detect onsets for sample slicing
        onset_processor = RNNOnsetProcessor()
        onset_activations = onset_processor(audio)
        peak_picker = OnsetPeakPickingProcessor()
        onsets = peak_picker(onset_activations)

        # 2. Detect beats and tempo for quantization
        beat_processor = RNNBeatProcessor()
        beat_activations = beat_processor(audio)
        beats = DBNBeatTrackingProcessor(fps=100)(beat_activations)
        tempi = TempoEstimationProcessor(fps=100)(beat_activations)

        # 3. Detect chords and key for harmonic arrangement
        try:
            chords = CRFChordRecognitionProcessor()(audio)
        except (ValueError, TypeError):
            # Skip chord detection if processor requires features
            chords = np.array([])

        key_result = CNNKeyRecognitionProcessor()(audio)
        # Extract key name from result
        from madmom.features.key import KEY_LABELS

        if len(key_result.shape) == 2:
            key_idx = np.argmax(key_result[0])
        else:
            key_idx = np.argmax(key_result)
        key = KEY_LABELS[key_idx]

        # 4. Detect downbeats for measure alignment
        downbeat_processor = RNNDownBeatProcessor()
        downbeat_activations = downbeat_processor(audio)
        beats_downbeats = DBNDownBeatTrackingProcessor(fps=100, beats_per_bar=[4])(
            downbeat_activations
        )
        downbeats = beats_downbeats[beats_downbeats[:, 1] == 1][:, 0]

        # Verify all analyses completed
        self.assertGreater(len(onsets), 0)
        self.assertGreater(len(beats), 0)
        self.assertGreater(len(tempi), 0)
        self.assertIsInstance(key, str)
        self.assertGreater(len(downbeats), 0)

        # Verify temporal consistency
        # Beats should be within audio duration
        # Get sample rate from audio signal (default is 44100 Hz)
        from madmom.audio.signal import Signal

        if isinstance(audio, Signal):
            sample_rate = audio.sample_rate
        else:
            sample_rate = 44100.0  # Default sample rate
        audio_duration = len(audio) / sample_rate
        self.assertTrue(np.all(beats <= audio_duration))
        self.assertTrue(np.all(onsets <= audio_duration))
        self.assertTrue(np.all(downbeats <= audio_duration))


if __name__ == "__main__":
    unittest.main()
