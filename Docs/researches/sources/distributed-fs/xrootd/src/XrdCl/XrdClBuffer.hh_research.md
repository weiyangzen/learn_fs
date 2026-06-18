# sources/distributed-fs/xrootd/src/XrdCl/XrdClBuffer.hh

Purpose: provides an owning binary buffer with an append cursor for XrdCl messages and related payloads.

Important APIs/types: constructors, move assignment, `Allocate`, `ReAllocate`, `Free`, `Zero`, `GetBuffer`, `GetSize`, `GetCursor`, `SetCursor`, `AdvanceCursor`, `Append`, `GetBufferAtCursor`, `FromString`, `ToString`, `Grab`, `Release`, and protected `Steal`.

Control flow/state: memory is managed with `malloc/realloc/free`; copies are disabled and moves transfer pointer, size, and cursor. `Append` grows the buffer as needed and advances the cursor; offset append does not move the cursor. `Grab` takes ownership of externally allocated memory expected to be `free`-compatible; `Release` transfers ownership out. Dependencies are C allocation/string headers and exceptions. Risks: `GetBuffer` can return null+offset when empty, `ToString` truncates at embedded NUL by constructing from C string, `realloc` failure loses original pointer, and `Grab` allocator mismatch. Test signals: move lifecycle, append growth, release ownership, binary strings with NUL bytes, and allocation failure behavior.
