# sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/SMB2FileIntegrationTest.java

Source read signal: reviewed complete local file (463 lines, 24680 bytes).

## Purpose
`SMB2FileIntegrationTest.java` covers SMB2 file integration tests. exercises opening, creating, checking existence, nested reads, share-mode locking, large transfer, byte-range locks, file ID lookup, append, server-side remote copy, delete-pending handling, async writes, and stream-based gzip/unzip transfer.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Tests use `DiskShare.openFile`, `File.write`, input/output streams, `ArrayByteChunkProvider`, `InputStreamByteChunkProvider`, `requestLock()`, remote copy, `deleteOnClose`, futures, and `endOfFile()` comparisons.

## State and persistence
State includes temporary files in `user`, seeded files in `public`, large random byte arrays, temp local gzip files, locks, and pending asynchronous write operations.

## Dependencies and integration points
Depends on access masks, share access, create dispositions, SMB status mapping, directory/file information classes, Apache Commons IO, Java streams, and the Samba container.

## Risks
Large transfer and async tests are timing/resource sensitive. Sharing-violation expectations depend on server lock/share-mode implementation. Temp-file cleanup occurs in `finally` for gzip tests.

## Test signals
Signals are byte-for-byte reads, matching file IDs, expected `STATUS_SHARING_VIOLATION`, successful locks/unlocks, completed async writes, and matching unzipped data.
