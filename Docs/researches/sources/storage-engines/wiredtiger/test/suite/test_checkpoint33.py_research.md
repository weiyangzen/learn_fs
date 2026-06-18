# sources/storage-engines/wiredtiger/test/suite/test_checkpoint33.py

Purpose: verifies checkpoint does not skip tables whose end-of-file free space can be reclaimed after checkpoint cleanup, and that repeated checkpointing can shrink a fully deleted table to minimum size.

Important APIs and types: `test_cc_base` checkpoint-cleanup helper, `suite_subprocess`, `stat.dsrc.block_size`, timestamped populate/delete loops, eviction cursor `debug=(release_evict)`, and `wait_for_cc_to_run`.

Control flow: create and populate a large table at timestamp 2, checkpoint at stable 3, delete all keys at timestamp 4, checkpoint at stable 5, evict all pages, advance oldest to 5, then loop waiting for checkpoint cleanup and checkpointing until file size drops below 12KB or max attempts.

State and persistence behavior: deletion becomes globally visible, checkpoint cleanup removes obsolete pages, and checkpoint should rewrite/truncate to reclaim file-end space.

Dependencies and integration points: integrates checkpoint cleanup with block manager truncation and statistics. Skips under TSan due to known compression-size failure.

Risks: high data volume and per-key transactions make it expensive. File size expectations depend on allocation/page layout and checkpoint cleanup timing.

Test signals: final `block_size` is less than or equal to `min_file_size`.
