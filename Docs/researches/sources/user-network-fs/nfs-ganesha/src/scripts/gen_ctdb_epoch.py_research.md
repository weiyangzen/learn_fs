# sources/user-network-fs/nfs-ganesha/src/scripts/gen_ctdb_epoch.py

## Purpose

`gen_ctdb_epoch.py` generates a cluster-safe 32-bit Ganesha epoch for CTDB environments by combining a CTDB node ID with a per-node generation counter.

## Important APIs, Types, and Functions

`main` increments a generation ID, masks it to 16 bits, reads the CTDB node ID, combines `nodeid << 16 | genid`, and prints it. `get_genid` reads `/var/lib/nfs/ganesha/seq_num`; `put_genid` writes it; `get_nodeid` runs `/usr/bin/ctdb pnn`.

## Control Flow

On execution, `main` reads/updates the generation file and invokes CTDB. Exceptions are caught in the `__main__` block, logged to syslog with traceback, and cause exit status 1.

## State and Persistence Behavior

The persistent state is `/var/lib/nfs/ganesha/seq_num`, storing the last generation number. The script mutates this file on every successful run.

## Dependencies and Integration Points

It depends on `/usr/bin/ctdb`, writable `/var/lib/nfs/ganesha`, Python subprocess APIs, and syslog. It is integrated through startup configuration such as `EPOCH_EXEC`.

## Risks and Edge Cases

There is no file locking despite importing `fcntl`; concurrent invocations can lose increments. If CTDB output is non-numeric, `int(nodeid)` fails. Generation wraps at 16 bits. The generation file write is not atomic or fsynced.

## Test Signals

Tests should mock `ctdb pnn`, use a temporary sequence file, verify initial/multiple/wrap values, and simulate concurrent calls if the script is hardened.
