# sources/storage-engines/wiredtiger/test/suite/test_prepare38.py

## Purpose

Checks compatibility: a database containing on-disk prepared updates produced with preserve-prepared can be opened with `preserve_prepared=false`.

## Important APIs, Control Flow, and State

The test creates a table, commits key 1, then in a prepared transaction removes key 1, inserts key 2, and inserts/removes key 3. It prepares at timestamp 10 with a prepared ID, advances stable to 20, checkpoints from another session to write prepared updates to disk, copies the WiredTiger home to `RESTART`, and opens that copy with `preserve_prepared=false`. Back in the original connection it rolls back the prepared transaction at timestamp 30 and advances stable.

## Dependencies, Risks, and Test Signals

Dependencies are `copy_wiredtiger_home`, alternate `wiredtiger_open`, preserve-prepared base config, and prepared IDs. The risk is an on-disk format compatibility break between preserve-prepared and normal opens. The signal is successful open of the copied home without preserving prepared state.
