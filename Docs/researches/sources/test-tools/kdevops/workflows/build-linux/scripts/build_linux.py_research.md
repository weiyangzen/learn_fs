# sources/test-tools/kdevops/workflows/build-linux/scripts/build_linux.py

## Purpose
Runs repeated Linux kernel builds and records timing/statistics, supporting out-of-tree builds, optional git tag checkout, cleaning between iterations, and `/usr/bin/time -v` logs.

## Important APIs, Types, and Functions
Main type is `LinuxBuilder` with methods `run_command`, `get_latest_tag`, `is_git_writable`, `checkout_tag`, `configure_kernel`, `clean_build`, `build_kernel`, `save_results`, and `run`. `main()` parses build/source/results/count/jobs/target/tag flags.

## Control Flow
The runner selects latest/custom tag, checks out if writable, configures the kernel if needed, loops builds, records duration and exit code, sleeps between iterations, then writes raw and summary JSON.

## State and Persistence Behavior
Creates results directory, `build_N.log`, `build_times_<hostname>.json`, and `summary_<hostname>.json`. It may modify source git state and can remove all out-of-tree build contents or run `git clean -f -x -d` in-tree.

## Dependencies and Integration Points
Requires Linux source, make, git, optional `/usr/bin/time`, and Python stdlib. Consumed by build-linux Ansible roles and downstream result scripts.

## Risks and Edge Cases
Uses `shell=True` with interpolated paths/targets. `rm -rf *` makes correct build-dir selection critical. Read-only source trees skip checkout and may build unexpected revisions. Systematic build failures do not abort the loop.

## Test Signals
Test count 1, read-only source, missing `.config`, failing target, jobs auto mode, clean-between, and JSON schema compatibility.
