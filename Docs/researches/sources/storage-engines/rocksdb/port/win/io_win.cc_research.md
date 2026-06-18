# sources/storage-engines/rocksdb/port/win/io_win.cc

Purpose: implements Windows file objects backing RocksDB's `FSSequentialFile`, `FSRandomAccessFile`, `FSWritableFile`, `FSRandomRWFile`, memory-mapped buffers, directories, and file locks.

Important APIs/types/functions: `GetWindowsErrSz`, `IOErrorFromWindowsError`, `pread`, `pwrite`, `fallocate`, `ftruncate`, `GetUniqueIdFromFile`, `WinFileData`, `WinMmapReadableFile`, `WinMmapFile`, `WinSequentialFile`, `WinRandomAccessImpl`, `WinRandomAccessFile`, `WinWritableImpl`, `WinWritableFile`, `WinRandomRWFile`, `WinMemoryMappedBuffer`, `WinDirectory`, and `WinFileLock`.

Control flow: reads/writes use `ReadFile`/`WriteFile`, sometimes with `OVERLAPPED` offsets to emulate POSIX `pread`/`pwrite`. Mmap writes preallocate, create/resize mapping handles, map fixed-size views, append via `memcpy`, flush page ranges, and truncate on close. Direct-I/O paths assert sector-aligned offsets, sizes, and buffers. Writable close flushes file buffers and closes handles.

State and persistence behavior: `WinFileData` owns a Windows file handle and direct-I/O/sector metadata. Writable classes track `next_write_offset_`, reserved size, mmap view state, pending sync state, and mapping handles. `Sync`/`Fsync` call `FlushFileBuffers` or `FlushViewOfFile`; close paths release handles and mapping views.

Dependencies and integration points: constructed by `WinFileSystem` in `env_win.cc`; used by RocksDB file readers/writers, table cache, WAL, manifest, and random-RW code. Uses `IOSTATS_TIMER_GUARD` and sync-point test hooks.

Risks and test signals: `GetUniqueIdFromFile` returns 0, reducing cross-reader cache sharing. Direct I/O alignment is enforced mostly by assertions. Mmap append pads to pages and truncates on close, so close/sync tests matter. Fault-injection, file reader/writer, WAL, table, and direct-I/O tests are important.
