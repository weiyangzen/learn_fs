# File Research: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/rndrm00.c

## Purpose
Random directory/file create-remove stress with growth and shrink phases.

## Key Elements
Creates `rndrm00_test_dir_<pid>`, grows by favoring creates over removes until threshold/full, shrinks by favoring removes until below threshold, repeats with optional sleep, then clears and removes the directory.

## Dependencies
Uses shared random entry and cleanup helpers from `tests.h`.

## Behavior/Risks
With `-z0`, the grow phase can fill the filesystem. `tests_remove_entry()` assumes there is at least one removable entry when asked to remove.
