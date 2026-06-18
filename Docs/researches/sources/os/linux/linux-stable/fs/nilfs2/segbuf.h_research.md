# File Research: sources/os/linux/linux-stable/fs/nilfs2/segbuf.h

`segbuf.h` defines in-memory segment summary and segment buffer structures. `struct nilfs_segsum_info` tracks flags, file-info count, block counts, summary bytes, file block count, segment sequence, checkpoint number, creation time, and next segment block. `struct nilfs_segment_buffer` adds superblock back pointer, list linkage, segment numbers/ranges, partial segment start, remaining blocks, summary/payload buffer lists, optional super-root buffer, and BIO completion/error fields.

The header provides list macros for segment buffers and buffer-head traversal through `b_assoc_buffers`. Inline helpers classify a partial segment as simplex (`LOGBGN|LOGEND`) or empty, and add summary, payload, and file buffers while updating block counters. File-buffer addition takes an extra buffer reference and increments the file-block count.

Declared APIs cover segment-buffer allocation/freeing, mapping, next-segment setup, reset, extension, summary fill, log-list cleanup/truncation/destruction, write/wait, and checksum application. It also declares the slab cache `nilfs_segbuf_cachep`, created in `super.c`.

This header is shared primarily by `segment.c`, `recovery.c`, and `segbuf.c`, defining the transport object for NILFS log writes.
