# sources/storage-engines/wiredtiger/test/csuite/wt3338_partial_update/main.c

## Purpose
WT-3338 stress-tests partial update construction and application. It compares WiredTiger's modify application and `wiredtiger_calc_modify` output with the independent `testutil_modify_apply` helper.

## Important APIs, Types, and Functions
- Uses global `WT_MODIFY entries[MAX_MODIFY_ENTRIES]`, random state, and replacement byte buffer.
- `modify_build` creates random modify vectors, including zero-length data and zero-size replacements.
- `compare` reports the first mismatch and dumps original/local/library buffers.
- `modify_run` constructs a fake `WT_CURSOR`, calls `__wt_modify_apply_api`, `testutil_modify_apply`, and `wiredtiger_calc_modify`.
- Uses internal buffer APIs `__wt_buf_set` and `__wt_buf_free` through `WT_SESSION_IMPL`.

## Control Flow
After opening a WiredTiger connection/session, `modify_run` initializes replacement data and loops 10,000 outer runs. Each outer run starts from a random short initial value and performs 1000 inner mutation rounds. For each round, it lowercases the current value, copies it, applies random modify vectors via WiredTiger and testutil implementations, compares results, asks WiredTiger to calculate a modify vector from the old to new value, applies that vector, and compares again. `WT_NOTFOUND` from `wiredtiger_calc_modify` is treated as no useful modify vector and skipped.

## State and Persistence Behavior
The test does not create application tables; it uses a real session only to support internal buffer and modify logic. The mutable state is the in-memory WT_ITEM buffers and fake cursor value.

## Dependencies and Integration Points
This is tightly coupled to WiredTiger internals (`WT_SESSION_IMPL`, `__wt_modify_apply_api`) and test utility modify semantics. It validates both the public `wiredtiger_calc_modify` API and lower-level apply path.

## Risks and Test Signals
Any divergence between local and library modify results aborts with detailed buffers. Random vectors exercise overlapping, empty, insertion, deletion, and replacement cases, but exact coverage depends on RNG. Because it creates no persistent table, it does not validate reconciliation or recovery of modifies.
