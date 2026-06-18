# sources/test-tools/lcov/tests/lcov/multiple/multiple.sh

## Purpose

`multiple.sh` tests initial coverage capture across multiple directories and case-insensitive source lookup behavior.

## Important APIs, types, and functions

It uses `common.tst`, `CC`, `LCOV_TOOL`, `GENINFO_TOOL`, `COVER`, `KEEP_GOING`, and `LCOV_OPTS="$PARALLEL $PROFILE"`. It invokes `lcov --capture --initial --no-external -d a -d b`, direct `geninfo --initial --no-external a b`, `--rc case_insensitive=1`, and `--no-markers`.

## Control flow

The script detects compiler versions and skips all initial-capture checks for GCC 5 and 6. It creates `rundir/a` and `rundir/b`, writes trivial `a.c` and `b.c`, compiles each in its own directory, captures initial coverage with multiple `-d` arguments, and expects two source records. It then captures with direct `geninfo` and expects identical output. For GCC 9+, it renames `b` to `B`, verifies normal capture only finds one source, then enables `case_insensitive=1` and expects output identical to the original two-directory capture.

## State and persistence behavior

It creates `rundir`, nested source/object/coverage files, and several `.info` outputs. It removes `rundir` at startup and supports clean-only mode.

## Dependencies and integration points

It depends on GCC coverage metadata path encoding, filesystem case behavior, LCOV/geninfo multi-directory input, and common harness helpers.

## Risks and test signals

This test is compiler- and filesystem-sensitive. Signals are `SF:` counts, exact `diff` equality between LCOV and geninfo, and recovery of renamed-case paths when `case_insensitive=1` is enabled.
