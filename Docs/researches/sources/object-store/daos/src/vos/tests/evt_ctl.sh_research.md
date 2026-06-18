# sources/object-store/daos/src/vos/tests/evt_ctl.sh

## Purpose
Shell harness that runs `evt_ctl` through a long deterministic scripted evtree workload, then runs built-in tests and drain tests. It also wraps the command with valgrind when requested.

## Important APIs, types, and functions
- Environment `USE_VALGRIND` selects memcheck or pmemcheck command prefixes.
- Sources `.build_vars.sh` to locate `$SL_PREFIX/bin/evt_ctl`.
- `word_set()` appends repeated add/find/delete/list patterns with overlapping extents and epochs.
- `check_max()` appends boundary-style max-extent checks.
- Final phases run scripted sequence, internal `-t` suite, and a drain command.

## Control flow
The script builds one long shell command string starting with `evt_ctl --start-test ... -C o:4`, appends loops of generated options, appends hand-written regression scenarios, executes it, checks status, then runs internal tests and drain tests similarly.

## State and persistence behavior
Runtime state is in the `cmd` shell variable and the PMEM/test files created by `evt_ctl`. The script itself persists no data, but valgrind memcheck may emit XML files named `unit-test-evt_ctl-%p.memcheck.xml`.

## Dependencies and integration points
Depends on bash, `.build_vars.sh`, the built `evt_ctl` binary, optional valgrind suppressions, and evt_ctl option grammar. It is a higher-level test entry used by DAOS test automation.

## Risks and edge cases
It uses `eval "$cmd"`, so command construction must remain controlled. Long command lines may hit shell/system limits if expanded further. `PIPESTATUS[0]` is used even though no explicit pipe is present; it still works in bash but is unusual. Paths depend on build variables being present.

## Test signals
Signals are nonzero exit on scripted workload failure, internal test failure, or drain failure; printed commands aid reproduction.
