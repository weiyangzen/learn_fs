# sources/storage-engines/rocksdb/file/file_util.cc

## Purpose
`file_util.cc` implements shared RocksDB file utilities for copying files, creating files, deleting DB files through optional `SstFileManager`, generating checksums, and recursively destroying directories.

## Important APIs and control flow
The first `CopyFile()` overload copies from a `FileSystem` source into an existing `WritableFileWriter`. It opens a `SequentialFileReader`, determines size when zero means "copy all", allocates a read buffer at least 4 KiB and at least `max_read_buffer_size`, then loops reading, checking for unexpected EOF, appending to the destination writer, and finally syncing with `use_fsync`. The second overload opens a destination `FSWritableFile`, wraps it in `WritableFileWriter`, and delegates.

`CreateFile()` opens a writable file, appends provided contents, and syncs. `DeleteDBFile()` and `DeleteUnaccountedDBFile()` route through `SstFileManagerImpl` scheduling unless forced foreground or no SFM exists, otherwise they call `Env::DeleteFile()`.

`GenerateOneFileChecksum()` validates and creates a checksum generator, verifies requested generator name when provided, opens a `RandomAccessFileReader`, computes file size, chooses a readahead buffer size with direct-I/O alignment, prepares `IOOptions`, reads the whole file in chunks, updates/finalizes the generator, and returns checksum plus function name. `DestroyDir()` recursively deletes children when `IsDirectory()` is supported and tolerates concurrent external deletion.

## State, persistence, and integration
These utilities perform real filesystem writes, syncs, deletes, and recursive removals. They integrate with `FileSystem`, `Env`, `SequentialFileReader`, `RandomAccessFileReader`, `WritableFileWriter`, `SstFileManagerImpl`, `IOTracer`, checksum factories, `RateLimiter`, statistics, and `ReadOptions`.

## Risks and test signals
The read buffer expression uses `max(4096, max_read_buffer_size)`, so a value named "max" actually acts as a minimum if larger than 4 KiB. Copy and checksum treat short reads before requested size as corruption. `DeleteDBFile()` assumes `sst_file_manager` is an `SstFileManagerImpl` when present. `DestroyDir()` ignores `IsDirectory()` unsupported, which can leave nested contents for filesystems without directory classification. Test signals are successful full/partial copy, checksum name mismatch failures, direct-I/O alignment coverage, read error/short-file corruption, SFM deletion routing, and recursive destroy under races.
