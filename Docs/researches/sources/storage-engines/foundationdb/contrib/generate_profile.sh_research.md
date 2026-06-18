# sources/storage-engines/foundationdb/contrib/generate_profile.sh

## Purpose
Shell helper to generate LLVM profile data for FoundationDB server and Mako workloads from a local build sandbox.

## Important APIs, Types, And Functions
Takes build directory and optional storage engine. Sets `LD_LIBRARY_PATH`, `FDB_CLUSTER_FILE`, and `LLVM_PROFILE_FILE`, launches `fdbmonitor`, configures a single-node database with `fdbcli`, runs Mako build/run workloads, forces `fdbserver` exit with `gdb`, kills `fdbmonitor`, then runs `llvm-profdata merge` into `fdb.profdata` and `mako.profdata`.

## Control Flow
Argument validation accepts one or two args. Default storage engine is `ssd`. Workload flow is start cluster, configure, generate client workload profiles, stop server to flush server profile, kill monitor, merge raw profiles.

## State And Persistence
Writes `.profraw` files under `$fdbdir/sandbox`, merged `$fdbdir/fdb.profdata`, and `$fdbdir/mako.profdata`. Starts and kills local FoundationDB processes.

## Dependencies And Integration
Requires a prepared FoundationDB build/sandbox, `fdbmonitor`, `fdbcli`, `mako`, `/proc`, `gdb`, and `llvm-profdata`. Linux-specific process discovery is used.

## Risks
No `set -euo pipefail`, so failures can cascade. Variables are unquoted. It uses `kill -9` and `gdb` attached to a child PID from `/proc`, which is Linux-specific and potentially hazardous if PID discovery is wrong. Existing profile files may be mixed with new output. The comment says CLI profile is ignored but still writes a raw file.

## Test Signals
Run in an isolated sandbox build, verify process cleanup and profile file creation, test missing binaries, invalid storage engine, failed configure, and repeated runs with stale `.profraw` files.
