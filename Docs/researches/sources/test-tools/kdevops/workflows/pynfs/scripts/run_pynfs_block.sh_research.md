<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/pynfs/scripts/run_pynfs_block.sh -->
# sources/test-tools/kdevops/workflows/pynfs/scripts/run_pynfs_block.sh

## Purpose
This script runs the pynfs NFSv4.1 pNFS block test set and writes a dedicated JSON result file. It complements the general v4.0/v4.1 runner with coverage for the block layout export.

## Important APIs and Variables
The script fixes `version="4.1"`, changes to `${PYNFS_DATA}/nfs4.1`, and invokes `./testserver.py`. Its output is `${PYNFS_DATA}/pynfs-block-results.json`; the export path is `"${EXPORT_BASE}-pnfs"`; the test selector is `block`.

## Control Flow
There is no loop or concurrency. The script performs a single directory change and a single testserver execution. The exit code is therefore controlled by `testserver.py` unless the `cd` command fails and the shell continues, because the script does not use `set -e`.

## State, Persistence, and Dependencies
The persistent state is the block-layout JSON result file. The script depends on the v4.1 pynfs checkout, the pNFS export name, root uid/gid test execution, and the server supporting the block test group.

## Risks and Test Signals
The unguarded `cd` means a missing pynfs directory can still lead to executing `./testserver.py` from the wrong directory if such a file exists. The script does not quote `PYNFS_DATA` in the `cd`. The primary test signal is whether the generated block result matches accepted pNFS behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/pynfs/scripts/run_pynfs_block.sh -->
