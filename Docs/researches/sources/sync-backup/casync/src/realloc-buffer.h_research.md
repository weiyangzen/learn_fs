# sources/sync-backup/casync/src/realloc-buffer.h

Purpose: declares the growable buffer structure and inline accessors.

Important APIs/types/functions: `ReallocBuffer` stores backing pointer, allocation, start offset, and end offset. Inline helpers return current data, offset data, size, append-one-byte, empty, and read-default wrappers; exported functions cover allocation, trimming, fd I/O, printf append, donation/steal, and byte search.

Control flow/state: callers commonly zero-initialize the struct, pass it by address, and eventually call `realloc_buffer_free`. `realloc_buffer_data` deliberately returns the buffer object itself for empty unallocated buffers so zero-length acquisitions can produce a non-NULL sentinel.

Dependencies/integration: includes `util.h` for assertions, types, and printf annotations.

Risks/test signals: inline assertions catch internal invariant breaks in debug/test builds. Holding pointers across subsequent buffer mutation is unsafe and should be avoided.

Source research group: `subset-b-009122`.
