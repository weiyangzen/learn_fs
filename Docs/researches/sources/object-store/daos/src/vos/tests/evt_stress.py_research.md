# sources/object-store/daos/src/vos/tests/evt_stress.py

## Purpose
Python stress wrapper for a specific `evt_ctl` pattern related to DAOS-11894. It generates hundreds of overlapping add operations to exercise evtree sort algorithms that previously segfaulted.

## Important APIs, types, and functions
- `EVTStress` parses `--algo` with choices `dist`, `dist_even`, and `soff`.
- Constructor walks upward from the script directory to find `.build_vars.json` and loads build paths.
- `run_cmd()` constructs an `evt_ctl` command using `${PREFIX}/bin/evt_ctl`, optional `-s <algo>`, creates order 23 tree, adds extents for starts 1 through 706, then debugs/destroys.

## Control flow
The script loads build configuration, formats a command string, appends a deterministic sequence of `-a start-1024@start` operations, and executes it with `os.system`.

## State and persistence behavior
No Python-side persistent state beyond loaded build config. The invoked `evt_ctl` creates and destroys its test tree/pool. Process exit is not explicitly propagated from `os.system` by `run_cmd`.

## Dependencies and integration points
Depends on Python stdlib, `.build_vars.json`, and the built `evt_ctl` binary. It integrates with evtree sorting feature flags through `evt_ctl -s`.

## Risks and edge cases
`os.system` return code is ignored, so callers may need to inspect process status externally. Command is string-built rather than argument-vector-based. Missing `.build_vars.json` raises `FileNotFoundError`.

## Test signals
Primary signal is whether `evt_ctl` completes without segfault for each sorting algorithm; output command/test name identifies the algorithm.
