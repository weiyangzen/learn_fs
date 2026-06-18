# sources/sync-backup/casync/src/reflink.h

Purpose: public declaration for reflink cloning support.

Important APIs/types/functions: declares `reflink_fd(source_fd, source_offset, destination_fd, destination_offset, size, ret_reflinked)` using `uint64_t` offsets and sizes.

Control flow/state: no in-memory state; operation mutates destination file extents and optionally reports successfully cloned bytes.

Dependencies/integration: included by extraction or cache code that can use kernel COW clones as a fast path before falling back to copy.

Risks/test signals: callers must treat unsupported reflink as a recoverable condition and preserve correctness with normal writes. Alignment and filesystem behavior are handled in the implementation.

Source research group: `subset-b-009122`.
