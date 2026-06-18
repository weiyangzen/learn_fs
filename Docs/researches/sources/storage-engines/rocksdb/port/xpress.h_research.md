# sources/storage-engines/rocksdb/port/xpress.h

Purpose: platform dispatch header for XPRESS compression.

Important APIs/types/functions: no direct functions; it includes `port/win/xpress_win.h` on Windows and errors on POSIX.

Control flow: compile-time platform guard rejects POSIX XPRESS and exposes Windows XPRESS declarations.

State and persistence behavior: none.

Dependencies and integration points: used by compression code that wants XPRESS only where implemented.

Risks and test signals: build configuration must not enable XPRESS on POSIX. Build matrix tests catch this.
