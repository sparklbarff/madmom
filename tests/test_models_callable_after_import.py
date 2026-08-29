"""madmom.models.models() must still work once the module has finished importing.

This is a different defect from the packaging one in test_model_constants_resolve.py, and it hides
in the same place. madmom/models/__init__.py ends with `del os, glob` to keep the package namespace
clean. The 20 model constants are assigned above that line, so they resolve while `glob` is still
bound and every one of them is correct. But `models()` is a public function that reads `glob` as a
global at CALL time, and by the time any caller can reach it the module body has run to completion
and unbound the name. So `models('beats/2019/*.pkl')` raised NameError rather than returning a list.

Why nothing caught it: every in-tree use reads the constants, never the function, so the whole test
suite passed and the package worked. It surfaced only when ruff was pointed at the tree and reported
F821, and it stayed invisible to the commit gate for a further reason worth recording: this file
lived behind a submodule gitlink until it was vendored, so `git ls-files madmom/models` returned one
entry and no hook could see the source at all.

The trap when testing this: importing madmom.models and calling models() inside the same test
process is not enough on its own to be convincing, because a reader cannot tell whether the call
succeeded for the right reason. So this asserts the specific mechanism too, that the module-level
names really are cleaned up, which is what made the original `del` tempting in the first place.
"""

from __future__ import annotations

import madmom.models


def test_models_is_callable_after_import():
    """The regression guard. Before the fix this raised NameError: name 'glob' is not defined."""
    found = madmom.models.models("beats/2019/beats_tcn_[1-8].pkl")
    assert isinstance(found, list), f"models() returned {type(found).__name__}, expected list"
    assert found, "models() returned an empty list for a pattern that matches vendored model files"


def test_models_returns_empty_list_for_a_pattern_that_matches_nothing():
    """A miss must come back as [] rather than raising.

    The distinction matters because the packaging bug fixed in 6a33225 depended on it: a constant
    whose files were not shipped resolved to [] and constructed fine, dying later with an IndexError
    naming neither the model nor the missing file. That behaviour is load-bearing for how the other
    test file reasons, so it is pinned here rather than assumed.
    """
    assert madmom.models.models("beats/1999/no_such_model_*.pkl") == []


def test_the_namespace_is_still_clean():
    """The fix must not be "delete the del". `os` and `glob` are still meant to be absent from the
    package namespace; the point is that models() no longer depends on one of them surviving."""
    for name in ("os", "glob"):
        assert not hasattr(madmom.models, name), (
            f"madmom.models.{name} is exposed; the namespace cleanup that motivated the original "
            f"`del os, glob` has been lost"
        )
