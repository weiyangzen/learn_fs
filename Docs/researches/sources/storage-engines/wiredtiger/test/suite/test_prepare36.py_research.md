# sources/storage-engines/wiredtiger/test/suite/test_prepare36.py

## Purpose

Verifies history-store contents for a committed prepared transaction under precise checkpoint and preserve-prepared.

## Important APIs, Control Flow, and State

The test writes baseline value A for keys 1 to 21 at timestamp 25, prepares value B for key 21 at timestamp 30, advances stable to 30, verifies checkpoint writes prepared metadata, evicts pages, and commits at 35/40. It reads key 21 at timestamp 40 as B and at timestamp 30 as A. When stable is 35, `check_ckpt_hs` opens `file:WiredTigerHS.wt` from the checkpoint and expects value A with start timestamp 25 and max stop timestamp. After stable 40 and reopen, it expects A in the history store with stop timestamp 40.

## Dependencies, Risks, and Test Signals

Dependencies are direct history-store cursor reads, `WT_TS_MAX`, preserve-prepared stats, eviction, and reopen. It skips disagg until cell packing/unpacking support exists. Risks are wrong HS stop timestamp adjustment around committed prepared updates. Signals are value/timestamp checks inside HS checkpoint and reopened HS files.
