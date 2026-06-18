# sources/storage-engines/wiredtiger/test/suite/test_leaf_delta_disagg01.py

## Purpose
Validates that disaggregated leaf page deltas merge correctly with a base image across overlapping updates, inserted keys, empty values, prefix compression, and deletes.

## APIs, Types, And Functions
Defines `test_leaf_delta_disagg01` with prefix-compression scenarios. Helpers build table config with `block_manager=disagg`, read data-source statistics, insert/update byte values, delete keys, verify present and deleted keys, and reopen disaggregated connections to force base-plus-delta reconstruction.

## Control Flow, State, And Persistence
`verify_leaf_delta` writes a base page, checkpoints, then reopens three times and writes three update batches, expecting one leaf delta per batch. It reopens again and verifies that latest deltas override earlier deltas and base entries. Individual tests vary duplicate key sets, new keys, empty values, and deletion. Delete testing adds one more checkpoint and verifies tombstone persistence after reopen.

## Dependencies, Integration, Risks, And Test Signals
Depends on `page_delta`, reconciliation statistics, prefix compression statistics, byte value format, and disaggregated block manager. Risks are wrong merge precedence, empty-value unpacking bugs, delta/delete tombstone mishandling, or prefix compression divergence. Signals include exact delta counts, prefix compression stat checks, and value/WT_NOTFOUND assertions after reopen.
