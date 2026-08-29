"""Performance benchmarks for madmom operations.

Tests performance of key operations to ensure optimizations are working.
"""

from __future__ import annotations

import time
import unittest
from pathlib import Path

import numpy as np

from madmom.audio import SignalProcessor
from madmom.features import (
    DBNBeatTrackingProcessor,
    RNNBeatProcessor,
    TempoEstimationProcessor,
)

from . import AUDIO_PATH

sample_file = Path(AUDIO_PATH) / "sample.wav"


class TestPerformance(unittest.TestCase):
    """Performance benchmarks for madmom operations."""

    def setUp(self):
        """Set up test fixtures."""
        if not sample_file.exists():
            self.skipTest(f"Test audio file not found: {sample_file}")

    def test_beat_tracking_performance(self):
        """Benchmark beat tracking performance."""
        audio = SignalProcessor()(str(sample_file))
        beat_processor = RNNBeatProcessor()
        beat_tracker = DBNBeatTrackingProcessor(fps=100)

        # Warm up
        activations = beat_processor(audio)
        _ = beat_tracker(activations)

        # Benchmark
        start_time = time.time()
        activations = beat_processor(audio)
        processing_time = time.time() - start_time

        start_time = time.time()
        beats = beat_tracker(activations)
        tracking_time = time.time() - start_time

        total_time = processing_time + tracking_time

        # Verify results
        self.assertGreater(len(beats), 0)

        # Performance expectations (should complete in reasonable time)
        # For a typical 3-minute song, beat tracking should take < 5 seconds
        from madmom.audio.signal import Signal

        if isinstance(audio, Signal):
            sample_rate = audio.sample_rate
        else:
            sample_rate = 44100.0  # Default sample rate
        audio_duration = len(audio) / sample_rate
        expected_max_time = max(
            5.0, audio_duration * 0.1
        )  # 10% of audio duration or 5s, whichever is larger

        self.assertLess(
            total_time,
            expected_max_time,
            f"Beat tracking took {total_time:.2f}s, expected < {expected_max_time:.2f}s",
        )

    def test_tempo_detection_performance(self):
        """Benchmark tempo detection performance."""
        audio = SignalProcessor()(str(sample_file))
        beat_processor = RNNBeatProcessor()
        tempo_processor = TempoEstimationProcessor(fps=100)

        # Warm up
        activations = beat_processor(audio)
        _ = tempo_processor(activations)

        # Benchmark
        start_time = time.time()
        activations = beat_processor(audio)
        processing_time = time.time() - start_time

        start_time = time.time()
        tempi = tempo_processor(activations)
        tempo_time = time.time() - start_time

        total_time = processing_time + tempo_time

        # Verify results
        self.assertGreater(len(tempi), 0)

        # Performance expectations
        from madmom.audio.signal import Signal

        if isinstance(audio, Signal):
            sample_rate = audio.sample_rate
        else:
            sample_rate = 44100.0  # Default sample rate
        audio_duration = len(audio) / sample_rate
        expected_max_time = max(3.0, audio_duration * 0.05)  # 5% of audio duration or 3s

        self.assertLess(
            total_time,
            expected_max_time,
            f"Tempo detection took {total_time:.2f}s, expected < {expected_max_time:.2f}s",
        )

    def test_batch_processing_performance(self):
        """Benchmark batch processing performance."""
        audio = SignalProcessor()(str(sample_file))
        beat_processor = RNNBeatProcessor()
        beat_tracker = DBNBeatTrackingProcessor(fps=100)

        # Process multiple times to simulate batch processing
        num_iterations = 5

        start_time = time.time()
        for _ in range(num_iterations):
            activations = beat_processor(audio)
            beats = beat_tracker(activations)
        total_time = time.time() - start_time

        avg_time = total_time / num_iterations

        # Verify results
        self.assertGreater(len(beats), 0)

        # Batch processing should be reasonably fast
        from madmom.audio.signal import Signal

        if isinstance(audio, Signal):
            sample_rate = audio.sample_rate
        else:
            sample_rate = 44100.0  # Default sample rate
        audio_duration = len(audio) / sample_rate
        expected_max_avg_time = max(5.0, audio_duration * 0.1)

        self.assertLess(
            avg_time,
            expected_max_avg_time,
            f"Average batch processing time: {avg_time:.2f}s, expected < {expected_max_avg_time:.2f}s",
        )

    def test_optimized_beat_detection(self):
        """Verify optimized beat detection is working."""
        # Test that detect_beats function works correctly (optimized version)
        from madmom.features.beats import detect_beats

        # Create synthetic activations with clear beat pattern
        fps = 100
        tempo = 120  # BPM
        interval = int(fps * 60 / tempo)  # frames per beat
        duration = 10  # seconds
        num_frames = fps * duration

        # Create activations with peaks at beat intervals
        activations = np.zeros(num_frames)
        for i in range(0, num_frames, interval):
            if i < num_frames:
                activations[i] = 1.0
                # Add some noise
                if i + 1 < num_frames:
                    activations[i + 1] = 0.5

        # Detect beats
        start_time = time.time()
        beats = detect_beats(activations, interval, look_aside=0.2)
        detection_time = time.time() - start_time

        # Verify results
        self.assertGreater(len(beats), 0, "Should detect at least one beat")
        self.assertLess(detection_time, 1.0, "Beat detection should be fast (< 1s)")

        # Verify beats are within valid range
        self.assertTrue(np.all(beats >= 0), "All beats should be non-negative")
        self.assertTrue(np.all(beats < num_frames), "All beats should be within activation range")

        # Verify beats are in ascending order
        if len(beats) > 1:
            self.assertTrue(np.all(np.diff(beats) > 0), "Beats should be in ascending order")


if __name__ == "__main__":
    unittest.main()
