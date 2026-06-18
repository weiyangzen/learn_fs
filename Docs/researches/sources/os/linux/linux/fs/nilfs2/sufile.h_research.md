# File Research: sources/os/linux/linux/fs/nilfs2/sufile.h

`sufile.h` declares the segment usage file API. It exposes segment count/clean count queries, allocation range control, segment allocation, dirty marking, usage live-block/time updates, stats retrieval, bulk suinfo get/set, resize, read/init, and TRIM support.

The update API allows callers to apply primitive operations to one or many segment numbers while holding the sufile metadata semaphore. Primitive functions include scrap, free, cancel-free, and set-error.

Inline wrappers provide semantic operations: `nilfs_sufile_scrap()`, `nilfs_sufile_free()`, `nilfs_sufile_freev()`, `nilfs_sufile_cancel_freev()`, and `nilfs_sufile_set_error()`. Their comments document expected error classes for invalid segment numbers, I/O/corruption, and allocation failures.
