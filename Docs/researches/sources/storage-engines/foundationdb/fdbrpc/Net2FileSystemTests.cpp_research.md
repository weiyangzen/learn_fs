# sources/storage-engines/foundationdb/fdbrpc/Net2FileSystemTests.cpp

`Net2FileSystemTests.cpp` validates asynchronous filesystem semantics required by FoundationDB.

The file defines `forceLinkNet2FileSystemTests()`, constants for 1 MiB and 4 KiB, and `writeRangeWithByte()` for repeated-pattern writes. Test cases are `/fileio/zero`, `/fileio/incrementalDelete`, `/fileio/rename`, and `/fileio/truncateAndRead`.

Control flow creates temporary files through `IAsyncFileSystem::filesystem()`, performs async sync, zero-range, writes, truncates, reads, renames, directory listing checks, and durable or incremental deletion. Assertions validate zero-filled data, successful large incremental delete, rename visibility and data preservation, and truncate extension zeroing.

State is real temporary filesystem state under `/tmp`. Some tests create large logical files, including about 5 GB and 100 MB files, and explicitly clear file references before rename/delete.

Dependencies include `IAsyncFile`, deterministic random, platform helpers, unit tests, aligned allocation, and whichever `IAsyncFileSystem` backend is registered. Risks include disk-space pressure, sparse-file differences, shared temporary filenames under parallel test execution, and platform-specific filesystem semantics. The listed test cases are the direct test signals.
