# sources/storage-engines/wiredtiger/test/csuite/wt3874_pad_byte_collator/main.c

## Purpose
WT-3874 verifies that removal with a custom collator respects logical key equality when padding bytes differ.

## Important APIs, Types, and Functions
- Defines `WT_COLLATOR my_coll` where `my_compare` compares only the first byte of each `WT_ITEM`.
- Uses a `key_format=u,value_format=u` table with `collator=my_coll`.
- Uses log-enabled WiredTiger open to put the scenario through normal logged table behavior.

## Control Flow
The test opens a clean home, registers the collator, creates `table:main`, inserts a 20-byte key whose first byte is `a` and remaining bytes are `X`, checkpoints, then changes the same buffer so the first byte remains `a` and padding becomes `Y`. It removes using the new logical key and closes.

## State and Persistence Behavior
The key and value share the same `WT_ITEM` buffer. A checkpoint persists the inserted version before removal. The removal must locate the stored key via collator semantics rather than raw byte equality.

## Dependencies and Integration Points
The test exercises C API collator registration, row-store key comparison, checkpointing, and cursor remove. It depends on the collator being consulted when matching keys fetched from storage.

## Risks and Test Signals
An assertion or remove failure indicates WiredTiger compared raw padded bytes where the collator should define equality. The test covers one simple key and does not reopen after removal.
