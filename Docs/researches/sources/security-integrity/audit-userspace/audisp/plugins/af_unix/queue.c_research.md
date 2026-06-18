## sources/security-integrity/audit-userspace/audisp/plugins/af_unix/queue.c

Purpose: simple fixed-capacity FIFO for AF_UNIX plugin output buffers.

`q_open` allocates queue metadata and slots, `q_append` copies or takes ownership of data, `q_peek` returns head pointer/length, `q_drop_head` frees and advances, and stats functions expose current/max/capacity. State is heap-backed circular buffer with per-entry data ownership. Dependencies are libc allocation and errno. Risks include no thread safety, overwrite leak if appending into a non-empty slot would occur due to logic bugs, caller must not mutate borrowed `q_peek` data, and fixed entry size rejects large records. Tests should cover full queue, oversized append, take-memory ownership, wraparound, and close cleanup.
