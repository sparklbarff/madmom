"""Every model constant must be covered by a package-data glob.

madmom/models/__init__.py names its model files as glob patterns, and pyproject.toml decides
which of those files a wheel actually contains. They are two independent lists that must agree,
and until 2026-08-19 nothing checked that they did. `models/beats/201[56]/*` matched the two
model years that existed when it was written and silently stopped at the third, so BEATS_TCN --
the default TCN beat tracker -- resolved to an empty list in every install. `models()` is
`return sorted(glob.glob(...))`, so a miss yields [] rather than raising: TCNBeatProcessor
constructs, reports nothing wrong, and dies later on use with an IndexError that names neither
the model nor the missing file.

The trap in testing this: importing madmom from the SOURCE tree resolves every constant against
the working directory, where all the .pkl files are present. Such a test passes while the wheel
ships nothing, which is the exact failure it was written to catch. So this compares the two
DECLARATIONS -- the patterns in __init__.py against the globs in pyproject.toml -- instead of
asking the filesystem whether files exist. It fails on a real install too, but it does not need
one to be correct.
"""

from __future__ import annotations

import glob
import os
import re
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MODELS_INIT = REPO / "madmom" / "models" / "__init__.py"
PYPROJECT = REPO / "pyproject.toml"

# BEATS_TCN uses double quotes, the rest single: match either.
_CONSTANT_RE = re.compile(r"^([A-Z][A-Z0-9_]*)\s*=\s*models\(\s*['\"](.+?)['\"]", re.MULTILINE)


def _declared_constants() -> list[tuple[str, str]]:
    """(name, glob pattern) for every `NAME = models('pattern')` in madmom/models/__init__.py."""
    return _CONSTANT_RE.findall(MODELS_INIT.read_text())


def _package_data_globs() -> list[str]:
    """The `madmom` package-data patterns from pyproject.toml."""
    with PYPROJECT.open("rb") as fh:
        data = tomllib.load(fh)
    return data["tool"]["setuptools"]["package-data"]["madmom"]


def _matches(pattern: str, path: str) -> bool:
    """Segment-wise glob match.

    Deliberately NOT fnmatch: its `*` crosses `/`, so `models/*/*` would appear to cover
    `models/beats/2019/x.pkl` and the check would pass on the very bug this file exists for.
    setuptools matches per path segment, so this does too.
    """
    pat_parts = pattern.split("/")
    path_parts = path.split("/")
    if len(pat_parts) != len(path_parts):
        return False
    from fnmatch import fnmatchcase

    return all(fnmatchcase(seg, pat) for pat, seg in zip(pat_parts, path_parts))


def test_every_model_constant_is_covered_by_a_package_data_glob():
    """The regression guard. A constant whose files no glob ships resolves to [] after install."""
    globs = _package_data_globs()
    uncovered: list[str] = []

    for name, pattern in _declared_constants():
        # Resolve the constant's pattern the way models() does, then ask whether each resulting
        # file would be packaged. Resolution uses the source tree only to enumerate the real
        # filenames; the assertion is about the globs, not about the files existing.
        base = MODELS_INIT.parent
        for abs_path in sorted(glob.glob(str(base / pattern))):
            rel = "models/" + os.path.relpath(abs_path, base).replace(os.sep, "/")
            if not any(_matches(g, rel) for g in globs):
                uncovered.append(f"{name} -> {rel}")

    assert not uncovered, "model files no package-data glob ships (they will be missing from an installed madmom):\n  " + "\n  ".join(
        uncovered
    )


def test_every_model_constant_resolves_to_at_least_one_file():
    """A constant pointing at a path that does not exist at all is a different defect from an
    unpackaged one, and models() reports neither: both come back as []."""
    empty = [
        f"{name} -> {pattern}"
        for name, pattern in _declared_constants()
        if not glob.glob(str(MODELS_INIT.parent / pattern))
    ]
    assert not empty, "model constants matching no file in the source tree:\n  " + "\n  ".join(empty)


def test_the_constant_scraper_actually_found_constants():
    """Guards the guard: if the regex stops matching, both tests above pass on an empty list and
    report success while checking nothing."""
    found = _declared_constants()
    assert len(found) >= 15, f"expected the full constant set, scraped only {len(found)}"
    assert any(name == "BEATS_TCN" for name, _ in found), "BEATS_TCN missing; regex drifted"
