# sources/storage-engines/wiredtiger/test/suite/test_checkpoint11.py

Purpose: timestamped version of inconsistent checkpoint visibility testing. It verifies checkpoint reads at explicit timestamps return complete valid states even when a timestamp-30 transaction commits during checkpointing.

Important APIs/types/functions: `checkpoint_thread`, `named_checkpoint_thread`, `stat.conn.checkpoint_state`, debug checkpoint cursor option `checkpoint_read_timestamp`, `SimpleDataSet`, scenario matrices for stable timestamp, overlap, advance, named/unnamed, and reopen behavior.

Control flow: set oldest/stable to 5, write full-table values at timestamps 10 and 20, checkpoint, prepare a large timestamp-30 transaction in another session, set stable to scenario value, start checkpoint thread, wait for checkpoint state, commit at 30, optionally reopen, build expected value-count maps for read timestamps 5/15/25/35 and default stable read, optionally advance timestamps to 50, then scan the checkpoint at each timestamp.

State/persistence behavior: validates checkpoint timestamp metadata and snapshot isolation under a concurrent commit. Default checkpoint read should reflect the stable timestamp at checkpoint creation.

Dependencies/integration: timestamped reads from checkpoints, slow checkpoint stress, named checkpoints, scenario filtering, and row/column formats.

Risks/test signals: crash/RTS crosscheck is disabled for reliability. Main failure is a torn value-count map at any timestamp.
