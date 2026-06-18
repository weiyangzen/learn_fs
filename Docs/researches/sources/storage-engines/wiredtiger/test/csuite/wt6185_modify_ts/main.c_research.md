# sources/storage-engines/wiredtiger/test/csuite/wt6185_modify_ts/main.c

## Purpose
WT-6185 verifies timestamped modify chains. It performs random modifies at increasing timestamps, rereads every committed version at its commit timestamp, and optionally forces eviction and checkpoints between operations.

## Important APIs, Types, and Functions
- Uses `WT_MODIFY`, `WT_RAND_STATE`, timestamped transactions, debug cursor eviction flags, and trace buffers.
- `modify_build` creates random modify vectors while preserving leading key-identifying bytes.
- `modify` performs up to four modifies in one transaction, optionally sets a read timestamp, commits at `ts + 1` or rolls back, and stores expected values in `list`.
- `repeat` rereads all committed expected values by `read_timestamp`.
- `evict` sets `WT_CURSTD_DEBUG_RESET_EVICT` around `cursor->reset` to force eviction.
- `trace_die` dumps operation history via `custom_die` on failure.

## Control Flow
The program parses local options for column-store mode, disabling checkpoint/eviction, preserving home, and RNG seed. It creates `file:xxx`, loads 101 records, closes/reopens, verifies a target record, and sets oldest timestamp to 1. For 250 runs, it resets trace state, performs 10 to 25 random modify operations on key 50, repeats historical reads after each operation, and randomly evicts or checkpoints depending on options. It prints one dot per run.

## State and Persistence Behavior
Persistent state includes one file with row or variable-length column keys. Timestamp state advances monotonically, with `oldest_timestamp=1`. The expected history list stores committed values and timestamps for the current run. Evictions and checkpoints force modify chains through reconciliation and disk state.

## Dependencies and Integration Points
The test depends on timestamp transactions, modify API, internal cursor debug eviction flags, and rollback/checkpoint behavior. The smoke wrapper runs both row and column modes.

## Risks and Test Signals
Any historical read mismatch triggers trace dumping. The random string length note documents a rare risk of exceeding trace buffer size. Options `-c` and `-e` can isolate checkpoint or eviction as failure contributors.
