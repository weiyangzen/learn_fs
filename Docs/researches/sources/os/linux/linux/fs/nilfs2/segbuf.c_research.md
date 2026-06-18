# File Research: sources/os/linux/linux/fs/nilfs2/segbuf.c

`segbuf.c` implements segment-buffer allocation, mapping, segment-summary construction, checksum filling, log BIO submission, and write completion waiting. Segment buffers are the in-memory representation of one partial segment being written.

`nilfs_segbuf_new()` allocates from `nilfs_segbuf_cachep`, initializes summary/payload lists, completion state, and I/O counters. Mapping helpers place a segment buffer either at a full segment plus offset or immediately after a previous partial segment. `nilfs_segbuf_reset()` starts a fresh summary block and initializes flags, checkpoint number, creation time, and counters.

`nilfs_segbuf_fill_in_segsum()` serializes the in-memory summary into the first summary block. CRC helpers compute and store summary checksum, payload checksum, and super-root checksum. Data CRC includes segment summary blocks and all payload buffer data.

Payload and summary buffer lists are released by `nilfs_clear_logs()` and `nilfs_truncate_logs()`. `nilfs_add_checksums_on_logs()` walks all logs and fills super-root, summary, and data checksums before write submission.

The write path batches sequential segment buffers into BIOs using `bio_alloc()`, `bio_add_folio()`, and `submit_bio()`. Completion increments `sb_err` on I/O failure and signals `sb_bio_event`; `nilfs_segbuf_wait()` waits for all BIOs and returns `-EIO` if any failed.
