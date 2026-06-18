<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/pynfs/scripts/run_pynfs.sh -->
# sources/test-tools/kdevops/workflows/pynfs/scripts/run_pynfs.sh

## Purpose
This shell script runs pynfs server tests for both NFSv4.0 and NFSv4.1 in parallel and writes JSON result files under `$PYNFS_DATA`. It is the workflow runner that generates the current result artifacts consumed by baseline comparison.

## Important APIs and Variables
The script depends on environment variables `PYNFS_DATA` and `EXPORT_BASE`. It defines two parallel arrays: `vers=("4.0" "4.1")` and `flags=("all" "all deleg xattr")`. For each version it changes directory to `${PYNFS_DATA}/nfs${version}` and runs `./testserver.py` with `--json`, `--maketree`, `--uid=0`, `--gid=0`, the export path, and the per-version flags.

## Control Flow
The first loop starts both pynfs invocations in the background. It increments an array index so v4.0 receives `all` and v4.1 receives `all deleg xattr`. The second loop calls `fg || true` once per version to wait for background jobs through shell job control.

## State, Persistence, and Dependencies
Persistent outputs are `${PYNFS_DATA}/pynfs-4.0-results.json` and `${PYNFS_DATA}/pynfs-4.1-results.json`. The script assumes job control is available (`set -m`), `testserver.py` exists in each pynfs checkout, exports are mounted or reachable at `${EXPORT_BASE}-${version}`, and the shell can foreground background jobs.

## Risks and Test Signals
The use of `fg || true` suppresses failures while waiting, so a failing pynfs run may not fail the script directly. Missing quotes around environment-expanded paths can break on spaces. Because both runs execute concurrently, shared server/export resources can introduce cross-test interference. Test signal comes from the JSON result files rather than the script exit status.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/pynfs/scripts/run_pynfs.sh -->
