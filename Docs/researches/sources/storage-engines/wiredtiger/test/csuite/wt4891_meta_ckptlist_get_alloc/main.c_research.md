# sources/storage-engines/wiredtiger/test/csuite/wt4891_meta_ckptlist_get_alloc/main.c

## Purpose
WT-4891 reproduces a metadata checkpoint-list allocation/verification path by keeping multiple checkpoint cursors open and then running `verify`.

## Important APIs, Types, and Functions
- Uses `CHECKPOINT_COUNT` set to 10.
- Uses `WT_CURSOR` for normal table updates and checkpoint cursors.
- Calls `session->checkpoint`, `session->open_cursor(..., "checkpoint=WiredTigerCheckpoint", ...)`, and `session->verify`.

## Control Flow
The test opens a clean home, creates a string-key/integer-value table, and opens a normal cursor. Ten times, it updates `key1` inside a snapshot transaction, checkpoints, and opens a checkpoint cursor to keep that checkpoint active. It closes the session, opens a new session, and verifies the table.

## State and Persistence Behavior
The same key is updated across ten checkpoints. Checkpoint cursors pin checkpoint metadata until the first session closes. The test is aimed at memory allocation behavior observable especially in sanitizer builds.

## Dependencies and Integration Points
It integrates with WiredTiger metadata checkpoint list retrieval and `__wt_verify` through the public `session->verify` entry point.

## Risks and Test Signals
Failures include verify errors or sanitizer-detected allocation misuse. The test does not inspect values; persistence correctness is inferred from successful checkpoint cursor handling and verify.
