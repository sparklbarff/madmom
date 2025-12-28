# TODO Items for Future Enhancement

This document lists all TODO, FIXME, and HACK comments found in the madmom codebase, organized by module.

**Status**: Some TODOs have been completed (see CHANGES.rst). Remaining items are either:
- Design decisions requiring careful consideration
- Performance optimizations requiring benchmarking
- Features waiting on upstream dependencies
- Complex enhancements requiring domain expertise

## Features Module

### `madmom/features/beats.py`

1. **Line 492**: `TempoEstimationProcessor` usage
   - Consider using `TempoEstimationProcessor` directly instead of creating a new instance
   - Location: `BeatTrackingProcessor.process()` method

2. **Line 601**: `look_aside` vs `interval_sigma` parameter
   - Document the relationship between `look_aside` and `interval_sigma` parameters
   - Clarify when to use each parameter

3. **Line 1174**: First beat skipping behavior
   - Documented: Intentional first beat skipping in online mode for accuracy
   - This is intentional behavior, not a bug

### `madmom/features/beats_hmm.py`

4. **Line 460**: Sparse representation optimization
   - Consider operating directly on sparse representation for better performance
   - Location: Transition model computation

5. **Line 680**: Pattern file enhancement
   - Save the number of beats in pattern files to avoid manual specification
   - Would improve usability

### `madmom/features/downbeats.py`

6. **Line 214**: Length validation
   - ✅ **Completed**: Code already checks and repeats length 1 inputs to match `beats_per_bar`
   - Location: `SyncronizeFeaturesProcessor`
   - Implementation: Lines 215-223 handle length 1 inputs by repeating them

7. **Line 829**: Use `load_beats` function
   - ✅ **Completed**: Replaced `np.loadtxt(matches[0])` with `load_beats(matches[0])`
   - Location: `SyncronizeFeaturesProcessor`

8. **Line 1033**: Beat subdivisions extraction
   - Extract `beat_subdivisions` from somewhere (metadata?)
   - Currently requires manual specification

9. **Line 1190**: Generic extrapolation
   - Expand to generic extrapolation of values
   - Currently specific to beat positions

### `madmom/features/tempo.py`

10. **Line 500**: Performance optimization
    - Speed up tempo histogram computation
    - Location: `TempoHistogramProcessor`

### `madmom/features/onsets.py`

11. **Line 243**: Filter class design
    - Consider making filter its own class for configurability
    - Location: `SpectralOnsetProcessor`

12. **Line 284**: HPSS usage
    - Use Harmonic-Percussive Source Separation (HPSS) instead of simple temporal filtering
    - Would improve onset detection quality

13. **Line 927**: Averaging function exchangeability
    - Make the averaging function exchangeable (mean/median/etc.)
    - Location: `RNNOnsetProcessor`

14. **Line 1092**: Frame count minimum
    - Use at least 1 frame if any of these values are > 0?
    - Location: `CNNOnsetProcessor`

15. **Line 1144**: Frame count minimum
    - Use at least 1 frame if any of these values are > 0?
    - Location: `CNNOnsetProcessor` (duplicate of above)

### `madmom/features/notes.py`

16. **Line 188**: Frame count minimum
    - Use at least 1 frame if any of these values are > 0?
    - Similar to onset detection TODOs

### `madmom/features/__init__.py`

17. **Line 185**: File closing strategy
    - Check if closing the file is really the best option to avoid memory issues
    - Location: `Activations` class

18. **Line 247**: Return type decision
    - Should we return the data or the Activations instance?
    - Location: `Activations` loading

## Machine Learning Module

### `madmom/ml/nn/layers.py`

19. **Line 850**: Constant mode verification
    - Check if constant mode is correct in all cases
    - Location: Layer initialization

20. **Line 1085**: Constant mode appropriateness
    - Is constant mode the most appropriate?
    - Location: Layer configuration

### `madmom/ml/nn/__init__.py`

21. **Line 50**: Tuple checking robustness
    - FIXME: Checking for tuples may be a bit fragile
    - Location: `average_predictions` function
    - Note: This is a known limitation but works for current use cases

### `madmom/ml/gmm.py`

22. **Model compatibility**: Old model attributes
    - Documented TODOs related to old model compatibility:
    - `weights_`, `means_`, `covars_` attributes
    - Models need to be updated by loading and saving again

## Processors Module

### `madmom/processors.py`

23. **Line 502**: Input/output processor validation
    - Check the input and output processors
    - Location: `ParallelProcessor`

24. **Line 744**: Fancy initialization
    - Use `np.pad` for fancy initialization (can be done in `process()`)
    - Location: `SequentialProcessor`

25. **Line 883**: Frame size overwrite
    - FIXME: Overwrite the frame size with the maximum value of all used processors
    - Location: `SequentialProcessor`

## Audio Module

### `madmom/audio/signal.py`

26. **Line 211**: Weighted mixing
    - Add weighted mixing support
    - Location: Signal mixing

27. **Line 628**: Start/stop settings validation
    - FIXME: Start and stop settings are not checked
    - Location: Signal processing

28. **Line 926**: Hack removal
    - Update: Removing this hack again, since it seems that it is not needed
    - Location: Signal processing

29. **Line 1476**: Hop size type checking
    - Check float / int hop size; theoretically a float hop size should be possible
    - Location: Signal processing

30. **Line 1494**: PyAudio termination
    - Is this the correct place to terminate PyAudio?
    - Location: Audio I/O

### `madmom/audio/stft.py`

31. **Line 82**: Multi-channel support
    - Add multi-channel support
    - Location: STFT processing

32. **Line 603**: Circular shift recalculation
    - Just recalculate with `circular_shift` set?
    - Location: STFT processing

### `madmom/audio/hpss.py`

33. **Line 17**: Processor vs array class design
    - TODO: Keep this as Processors or should it be done as np.ndarray classes?
    - Design decision for HPSS implementation

### `madmom/audio/filters.py`

34. **Line 98**: Zwicker's formula
    - Use Zwicker's formula?
    - Location: Filter design

35. **Line 120**: Zwicker's formula inverse
    - Use Zwicker's formula? What's the inverse of the above?
    - Location: Filter design

36. **Line 782**: Filterbank value handling
    - If needed, allow other handling (like summing values)
    - Location: Filterbank processing

37. **Line 957**: Filterbank options list
    - Add a list with filterbank options
    - Location: Filterbank configuration

38. **Line 970**: Filterbank parameter naming
    - Add a second argument with `num_bands_per_octave` and rename the parameter
    - Location: Filterbank configuration

39. **Line 1342**: Comments addition
    - Add comments
    - Location: Filter implementation

40. **Line 1353**: Norm filters dependency
    - Check if this should depend on the `norm_filters` parameter
    - Location: Filter implementation

41. **Line 1453**: Multiple corner frequencies
    - Property should return multiple corner frequencies
    - Location: Filter property

42. **Line 1458**: Multiple center frequencies
    - Property should return multiple center frequencies
    - Location: Filter property

### `madmom/audio/cepstrogram.py`

43. **Line 56**: Frequency bin documentation
    - What are the frequencies of the bins?
    - Location: Cepstrogram processing

## I/O Module

### `madmom/io/audio.py`

44. **Line 125**: avconv bug workaround
    - RuntimeError raised: 'avconv has a bug, which results in wrong audio'
    - This is a known issue with avconv, not a TODO

45. **Line 341**: Debug verbosity
    - Uses `-v debug` for debugging
    - May want to make this configurable

### `madmom/io/midi.py`

46. **Line 20**: Unit conversion functions
    - TODO: Remove these unit conversion functions after upstream PR is merged
    - Waiting on upstream library update

47. **Line 224**: Method removal
    - TODO: Remove this method after upstream PR is merged
    - Waiting on upstream library update

48. **Line 296**: BPM return option
    - TODO: Add option to return in BPM
    - Location: MIDI processing

### `madmom/io/__init__.py`

49. **Line 439**: Hack-ish solution
    - TODO: This is kind of hack-ish, find a better solution
    - Location: File I/O

## Utils Module

### `madmom/utils/midi.py`

50. **Line 805**: Event handling
    - TODO: Is this needed, should be handled by Event already
    - Location: MIDI event processing

51. **Line 1221**: EndOfTrackEvent
    - TODO: Should we add an EndOfTrackEvent?
    - Location: MIDI track processing

52. **Line 1477**: Track type validation
    - TODO: Test if the items of the list are of type MIDITrack
    - Location: MIDI file processing

53. **Line 1484**: Format 2 playback
    - TODO: Format 2 has multiple tracks but plays them back one after another
    - Location: MIDI file format handling

### `madmom/utils/__init__.py`

54. **Line 596**: Comments addition
    - TODO: Add comments!
    - Location: Utility function

55. **Line 658**: Warning removal
    - TODO: Remove warning?
    - Location: Deprecated function

## Evaluation Module

### `madmom/evaluation/tempo.py`

56. **Line 139**: Error return
    - TODO: Also return the errors?
    - Location: Tempo evaluation

57. **Line 362**: Tempi evaluation
    - TODO: Add option to evaluate any other than the default number of tempi
    - Location: Tempo evaluation

### `madmom/evaluation/onsets.py`

58. **Line 66**: Multi-dimensional array support
    - TODO: Right now, it only works with 1D arrays
    - Location: Onset evaluation

### `madmom/evaluation/notes.py`

59. **Line 120**: Duration and velocity evaluation
    - TODO: Extend to also evaluate the duration and velocity of notes
    - Location: Note evaluation

60. **Line 163**: Octave error reporting
    - TODO: Extend to also report the measures without octave errors
    - Location: Note evaluation

### `madmom/evaluation/beats.py`

61. **Line 618**: Code removal
    - TODO: Remove this, see TODO below
    - Location: Beat evaluation

62. **Line 644**: First beat enforcement
    - TODO: As agreed with Matthew, this should only be enforced from the 2nd beat
    - Location: Beat evaluation

### `madmom/evaluation/__init__.py`

63. **Line 41**: Multi-dimensional array support
    - TODO: Right now, it only works with 1D arrays
    - Location: Evaluation function

64. **Line 91**: Multi-dimensional array support
    - TODO: Right now, it only works with 1D arrays
    - Location: Evaluation function

65. **Line 136**: Multi-dimensional array support
    - TODO: Right now, it only works with 1D arrays
    - Location: Evaluation function

66. **Line 172**: Multi-dimensional array support
    - TODO: Right now, it only works with 1D arrays
    - Location: Evaluation function

67. **Line 687**: SimpleEvaluation unification
    - TODO: Unify this with SimpleEvaluation but...
    - Location: Evaluation class

68. **Line 749**: Metrics dict usage
    - TODO: Use e.metrics dict?
    - Location: Evaluation processing

69. **Line 791**: Metrics dict usage
    - TODO: Use e.metrics dict
    - Location: Evaluation processing

70. **Line 792**: Generic totable function
    - TODO: Add a generic totable() function which accepts columns separator
    - Location: Evaluation output

## Summary

**Total TODOs/FIXMEs**: 70 items

**Categories**:
- **Performance optimizations**: ~5 items
- **API improvements**: ~10 items
- **Feature enhancements**: ~15 items
- **Code quality/refactoring**: ~20 items
- **Documentation**: ~5 items
- **Design decisions**: ~10 items
- **Upstream dependencies**: ~5 items

**Priority Areas**:
1. Performance optimizations (tempo histogram, sparse representations)
2. Multi-dimensional array support in evaluation functions
3. API consistency improvements
4. Design pattern improvements (HPSS, filter classes)
5. Documentation and comments

**Note**: These are enhancement opportunities, not bugs. The codebase is functional and all tests pass. These items represent potential improvements for future development.

