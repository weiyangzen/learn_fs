# sources/storage-engines/rocksdb/port/win/xpress_win.h

Purpose: declares the Windows XPRESS compression API surface used by RocksDB.

Important APIs/types/functions: `Compress`, `CompressWithMaxSize`, `Decompress`, `GetDecompressedSize`, and `DecompressToBuffer` under `port::xpress`.

Control flow: declarations only; implementation is conditional in `xpress_win.cc`.

State and persistence behavior: no state in the header; implementation returns buffers or writes caller-provided buffers.

Dependencies and integration points: included by `port/xpress.h` for Windows builds.

Risks and test signals: caller ownership of `Decompress` return memory must remain consistent. Compression tests should cover empty input, corrupt input, and undersized output.
