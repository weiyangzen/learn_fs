# File Research: sources/os/linux/linux/fs/nilfs2/segbuf.h

`segbuf.h` declares segment-buffer structures and list helpers. `struct nilfs_segsum_info` stores the in-memory summary fields later serialized into `struct nilfs_segment_summary`: flags, file-info count, total blocks, summary blocks, summary byte count, file-block count, segment sequence, checkpoint number, creation time, and next-segment block.

`struct nilfs_segment_buffer` tracks the mapped full segment, partial segment start, remaining blocks, summary buffers, payload buffers, optional super-root buffer, outstanding BIO count, error status, and completion event.

The header provides list macros for segment buffers and buffer-head lists, plus inline helpers for checking whether a log is “simplex” (`LOGBGN|LOGEND`), empty, and for adding summary, payload, or file buffers. Adding a file buffer takes an extra buffer reference and increments file-block accounting.

Public functions cover segment-buffer lifecycle, mapping, next-segment setup, summary/payload extension, summary serialization, log cleanup/truncation/destruction, log writing/waiting, and checksum insertion.
