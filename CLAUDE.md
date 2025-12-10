# madmom2025 - NumPy 2.x Compatible Fork

## Project Status

**Good news:** The upstream madmom repository already has NumPy 2.x compatibility!

The original maintainers merged PR #540 on 2024-08-25 which includes:
- Cython and NumPy 2 compatibility fixes
- Python 3.9-3.12 support
- `pyproject.toml` build configuration requiring `numpy>2`
- Various compatibility fixes for NumPy 2.1+

### Test Results (Python 3.14, NumPy 2.3.5, scipy 1.16.3)

- **811 passed** (100% pass rate)
- Test tolerance fixes applied for ffmpeg 8.x and scipy 1.16.x compatibility
- Core beat tracking, tempo detection, and feature extraction working correctly

## Repository Structure

```
madmom2025/
├── setup.py              # Legacy build (still functional)
├── pyproject.toml        # Modern build config (numpy>2)
├── madmom/
│   ├── audio/            # Audio loading, signal processing
│   │   └── comb_filters.pyx  # Cython extension
│   ├── features/         # Feature extraction (beats, chords, tempo)
│   │   └── beats_crf.pyx     # Cython extension
│   ├── ml/               # Machine learning, neural networks
│   │   ├── hmm.pyx           # Cython extension (HMM Viterbi)
│   │   └── nn/
│   │       └── layers.pxd    # Cython header
│   └── models/           # Pre-trained weights (git submodule)
├── tests/                # Test suite (811 tests)
└── bin/                  # CLI entry points
```

## Quick Start

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install in development mode
pip install -e .

# Verify installation
python -c "import madmom; print(madmom.__version__)"

# Run tests
pip install pytest
pytest tests/ -q
```

## Cython Extensions

Four Cython files requiring compilation:
1. `madmom/audio/comb_filters.pyx` - Feed-forward/backward comb filters
2. `madmom/features/beats_crf.pyx` - CRF beat detection Viterbi
3. `madmom/ml/hmm.pyx` - Hidden Markov Model implementation
4. `madmom/ml/nn/layers.pxd` - Neural network layer headers

All use `np.float_t` and `np.float32` (correct NumPy 2.x compatible dtypes).

## Git Remotes

- `origin`: https://github.com/sparklbarff/madmom.git (your fork)
- `upstream`: https://github.com/CPJKU/madmom.git (original)

## Remaining Work

### Completed
- [x] Test tolerance fixes for ffmpeg 8.x resampling differences (±1 LSB)
- [x] Test tolerance fixes for scipy 1.16.x chroma precision
- [x] Modernized pyproject.toml with full PEP 621 metadata

### Enhancements
- [ ] Add GitHub Actions CI for the fork
- [ ] Consider PyPI release under new name (madmom2025?)
- [ ] Add CHANGELOG documenting fork purpose

## Key Upstream Commits

- `27f032e` - CI and NumPy compatibility updates (#540) - 2024-08-25
- `04e108d` - numpy & scipy compatibility fixes - 2023-09-09

## Development Notes

The fork was created assuming madmom needed NumPy 2.x migration work, but the upstream maintainers already completed this. This fork can serve as:

1. A personal maintained copy if upstream becomes truly abandoned
2. A place to add enhancements not accepted upstream
3. A staging area for testing with newer Python versions (3.14+)

Current branch: `numpy2-migration`
