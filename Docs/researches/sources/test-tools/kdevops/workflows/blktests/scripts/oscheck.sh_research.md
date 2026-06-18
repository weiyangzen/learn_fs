# sources/test-tools/kdevops/workflows/blktests/scripts/oscheck.sh

## Purpose
Wraps upstream blktests `./check` with root enforcement, OS/kernel policy, test group inference, expunge flags, optional command display, and kernel log markers.

## Important APIs, Types, and Functions
Local functions are `oscheck_usage`, `copy_to_check_arg`, `parse_args`, `oscheck_run_cmd`, `oscheck_run_groups`, `_cleanup`, and `check_check`. Shared state comes from `oscheck-lib.sh`.

## Control Flow
The script requires root, sources the library, parses known options, passes unknown tokens to `./check`, verifies OS/kernel and group, checks for `./check`, computes expunges, builds the command, then prints or executes it under `LC_ALL=C`.

## State and Persistence Behavior
Writes `/tmp/run-cmd.txt` when executing and can write start/done markers to `/dev/kmsg`. Test result persistence is handled by blktests and kdevops roles.

## Dependencies and Integration Points
Requires a blktests tree, root privileges, bash, and `oscheck-lib.sh`. Integrated into kdevops blktests run tasks.

## Risks and Edge Cases
`CHECK_ARGS` is array-declared but string-appended, so arguments with spaces are unsafe. `DRY_RUN` and `ONLY_CHECK_DEPS` are unused. The trap references unset `$status`.

## Test Signals
Test non-root, missing `./check`, `--show-cmd`, `--expunge-list`, group selection, pass-through flags, distro-kernel query, and `/dev/kmsg` marker options.
