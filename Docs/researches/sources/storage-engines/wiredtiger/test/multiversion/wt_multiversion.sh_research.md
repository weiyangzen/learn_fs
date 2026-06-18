# sources/storage-engines/wiredtiger/test/multiversion/wt_multiversion.sh

## Purpose
This Bash script exercises WiredTiger workgen multiversion compatibility between the current checkout and an older stable WiredTiger release. It builds the last-stable tree on demand, copies the current multiversion runner into it, and runs release-specific compatibility checks.

## Important APIs, Types, and Functions
The script defines `last_stable=4.2`, `last_stable_dir=wiredtiger_4.2/`, and `last_stable_branch=mongodb-4.2`. `setup_last_stable` clones `https://github.com/wiredtiger/wiredtiger.git`, checks out the stable branch, runs `bash reconf`, configures with Python and diagnostic support, and builds with `make -j 10`. `run_check` echoes and executes a command, exiting on failure.

## Control Flow
If the stable tree does not exist, the script clones and builds it. It then sets paths for the current and stable `bench/workgen/runner/multiversion.py`, copies the current runner into the stable tree, and runs four checks: current runner for release 4.4, current runner with `--keep`, stable-tree runner with `--keep --release 4.2`, and current runner again with `--keep --release 4.4`. Success prints `Success.` and exits 0.

## State, Persistence, and Integration
The script creates a sibling `wiredtiger_4.2` directory and leaves it for reuse. It mutates that clone by copying the latest multiversion runner over the stable runner path. It depends on network access, Git, autotools/reconf prerequisites, Python support, diagnostic build support, and the relative location of `bench/workgen/runner/multiversion.py`.

## Risks and Test Signals
Risks include network or branch availability failures, build dependency drift, stale stable clone contents, relative path changes, and incompatibilities hidden by copying the current runner into the stable tree. The test signal is command exit status through `run_check`; the echoed commands identify which multiversion pass failed.
