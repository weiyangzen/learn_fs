# File Research: sources/os/linux/linux-stable/fs/nilfs2/segbuf.c

`segbuf.c` implements segment-buffer allocation, mapping, summary construction, CRC insertion, and BIO submission. A segment buffer represents one partial segment: summary buffers, payload buffers, optional super-root buffer, disk location, block counts, next segment pointer, and asynchronous BIO completion/error state.

Mapping helpers place a segment buffer either at a full segment and offset (`nilfs_segbuf_map`) or immediately after a previous partial segment (`nilfs_segbuf_map_cont`). `nilfs_segbuf_set_next_segnum()` stores the next full segment’s block address in the in-memory summary. Reset and extend helpers allocate summary/payload buffers from the block device mapping and update in-memory counts.

`nilfs_segbuf_fill_in_segsum()` writes the raw segment summary header fields: magic, bytes, flags, sequence, creation time, next block, block counts, file info count, summary byte count, padding, and checkpoint number. CRC helpers compute separate summary, data, and super-root checksums. Data CRC covers summary blocks and payload blocks by temporarily mapping payload folios.

Log list helpers clear/truncate/destroy segment buffers and write/wait across a list. `nilfs_add_checksums_on_logs()` applies all relevant checksums after payload writeback has been prepared by the segment constructor.

BIO submission uses `struct nilfs_write_info` to pack buffers into block-device write BIOs. Each BIO completion increments `sb_err` on failure and completes `sb_bio_event`. `nilfs_segbuf_write()` submits summary buffers followed by payload buffers, marking the final BIO `REQ_SYNC`; `nilfs_segbuf_wait()` waits for all outstanding BIOs and reports a log-write I/O error with start block, block count, and segment number.

This file does not decide what to write; `segment.c` builds the segment content and uses `segbuf.c` to serialize it to disk.
