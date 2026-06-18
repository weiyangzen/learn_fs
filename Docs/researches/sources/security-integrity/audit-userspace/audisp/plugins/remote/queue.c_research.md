# sources/security-integrity/audit-userspace/audisp/plugins/remote/queue.c

Purpose: implements a fixed-size string queue with optional in-memory cache, persistent file storage, locking, and resize support.

Important APIs and data: exports `q_open`, `q_close`, `q_append`, `q_peek`, `q_drop_head`, and `q_queue_length`. Persistent files contain a binary header with magic, version, entry count, entry size, queue head, and queue length in network byte order.

Control flow: `q_open` validates flags and sizes, initializes memory cache, opens or creates/validates the file, and performs resize by copying entries into a temporary queue then renaming. Append writes the tail entry and syncs header state; peek returns head from memory or file and drops corrupt unterminated entries; drop advances the circular head and syncs.

State and persistence: memory queue state is volatile; file queue state persists across restart and is protected by `lockf` process locking. Queue entries are fixed-size slots, with string payloads including trailing NUL.

Dependencies and integration: used by `audisp-remote.c` for remote spool. Depends on POSIX file I/O, optional `posix_fallocate`, syslog, and queue constants in `queue.h`.

Risks: `fdatasync` is only used when `Q_SYNC` is set; store-forward path does not set it by default, leaving crash windows. Persistent file format rejects entry-size changes and corrupt headers. The recursive corrupt-entry skip in `q_peek` could recurse through many bad entries.

Test signals: `test-queue.c` covers open flags, locking, empty behavior, data size limits, wraparound, reopen persistence, and resizing.
