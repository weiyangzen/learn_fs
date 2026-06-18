# sources/sync-backup/git-crypt/fhstream.cpp

Purpose: custom C++ stream buffer implementation that adapts arbitrary read/write callbacks into `std::ostream` and `std::istream` behavior for subprocess pipes.

Important APIs/types/functions: `ofhbuf` constructor/destructor, `overflow`, `sync`, `xsputn`, `setbuf`; `ifhbuf` constructor/destructor, `underflow`, `xsgetn`, and `setbuf`.

Control flow: output buffers accumulate writes until overflow/sync, then repeatedly invoke the write callback until all bytes are written. Large `xsputn` writes flush the buffer and write directly. Input underflow preserves a small putback area, reads from the callback, and exposes buffered bytes; large `xsgetn` copies remaining buffered data and then reads directly.

State/persistence behavior: state is heap-allocated buffers, callback handles, put/get pointers, and output buffering. There is no persistent file state; the callback target owns actual handles.

Dependencies/integration: used by `Coprocess` pipe streams. Relies on callback functions throwing exceptions on OS-level errors.

Risks/test signals: partial reads/writes and EOF behavior must match C++ stream expectations. Tests should cover small/large writes, explicit `sync`, unbuffered mode via `setbuf(0,0)`, putback after direct reads, EOF propagation, and exception behavior from callbacks.
