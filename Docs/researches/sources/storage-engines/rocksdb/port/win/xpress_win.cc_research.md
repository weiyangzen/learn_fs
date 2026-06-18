# sources/storage-engines/rocksdb/port/win/xpress_win.cc

Purpose: implements RocksDB's Windows XPRESS compression adapter using the Windows Compression API when `XPRESS` is enabled.

Important APIs/types/functions: `xpress::Compress`, `CompressWithMaxSize`, `Decompress`, `GetDecompressedSize`, and `DecompressToBuffer`.

Control flow: each operation creates a compressor or decompressor handle, wraps it in a RAII `unique_ptr`, calls `Compress`/`Decompress`, and handles the standard `ERROR_INSUFFICIENT_BUFFER` size-query pattern. Buffer-returning decompression allocates with `new[]` because callers delete with `delete[]`.

State and persistence behavior: stateless aside from transient compression handles and output buffers. No persistence.

Dependencies and integration points: included through `port/xpress.h` on Windows; integrates with RocksDB compression utilities when XPRESS is configured.

Risks and test signals: the implementation is absent unless both `OS_WIN` and `XPRESS` are defined. Error handling returns false/0/-1/null rather than `Status`. Compression round-trip and max-output-size tests are primary signals.
