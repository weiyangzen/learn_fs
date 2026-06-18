# File Research: sources/os/bsd/freebsd-src/sbin/ddb/ddb.conf

## Purpose
Default DDB script definitions loaded during multi-user startup.

## Main Elements
- Defines `lockinfo` script for lock and vnode diagnostics.
- Defines `kdb.enter.panic` script to enable textdump capture, collect CPU/backtrace/process/thread diagnostics, dump textdump, and reset.
- Defines `kdb.enter.witness` script to run lock diagnostics on witness locking errors.

## Dependencies And Integration
Intended to be piped through `ddb` by rc startup. Consumed by `ddb_readfile()` command parsing.

## Risk Notes
The panic script performs `reset` after textdump capture, so changing this file changes crash-time system behavior.
