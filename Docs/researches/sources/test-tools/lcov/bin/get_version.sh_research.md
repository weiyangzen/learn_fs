# sources/test-tools/lcov/bin/get_version.sh

## Purpose

`get_version.sh` prints LCOV version metadata in one of three forms: version, release, or full version string. It derives metadata from Git tags when available, from a packaged `.version` file when Git metadata is unavailable, and from hard-coded fallback defaults otherwise.

## Important APIs, types, and functions

This Bash script has no functions. It computes `DIRPATH`, `TOOLDIR`, and `GITVER=$(cd "$TOOLDIR" ; git describe --tags 2>/dev/null)`. If `GITVER` is empty and `../.version` exists, it `source`s that file. If Git metadata exists, it strips a leading `v`, extracts `VERSION` from the part before the first dash, and converts the first dash in the remaining suffix into a dot for `RELEASE`. Fallbacks set `VERSION=2.5.0`, `RELEASE=beta`, and `FULL="$VERSION-$RELEASE"`.

Supported outputs are selected by the first argument: `--version`, `--release`, or `--full`.

## Control flow

The script resolves its tool directory, tries Git tag description, fills version variables from Git or `.version`, applies fallback defaults, then conditionally echoes the requested value without a trailing newline. Unknown or missing arguments produce no output; there is no usage error path.

## State and persistence behavior

The script is read-only except for shell variables. It sources `../.version`, so that file can set or override shell variables in-process. It writes selected metadata to stdout and does not write files.

## Dependencies and integration points

Dependencies are Bash, `dirname`, `cd`, `pwd`, `git`, and an optional LCOV `.version` file containing shell assignments. It is likely called by build/release/manpage tooling and by `lcovutil` version discovery paths.

## Risks and edge cases

- Sourcing `.version` executes shell code from that file, which is normal for trusted release metadata but unsafe for untrusted trees.
- `git describe --tags` behavior depends on reachable tags; shallow or tagless clones fall back to `.version` or defaults.
- The Git parsing handles a single dash-based suffix conversion for `RELEASE`; unusual tag formats may produce surprising `FULL`/`RELEASE`.
- Unknown arguments silently succeed with no output because there is no final validation.
- Output uses `echo -n`, which is common but can vary in strict portability; Bash mitigates this.

## Test signals

Tests should cover Git-tagged checkout output, no-Git `.version` output, total fallback output, and each argument selector. Additional tests should verify unknown arguments produce empty output and that tags like `v2.5-3-gHASH` produce the expected `VERSION`, `RELEASE`, and `FULL`.
