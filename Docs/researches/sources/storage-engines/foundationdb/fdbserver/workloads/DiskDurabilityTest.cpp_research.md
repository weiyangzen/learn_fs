# sources/storage-engines/foundationdb/fdbserver/workloads/DiskDurabilityTest.cpp

Purpose: Implements `DiskDurabilityTest`, a database-backed durability ledger for a raw file. It verifies recorded pages, writes new pages, syncs the file, then records page values in FoundationDB.

Important APIs/types/functions: `DiskDurabilityTest`, `encodeValue`, `encodeKey`, `decodeValue`, `decodeKey`, `encodePage`, `decodePage`, `IAsyncFileSystem::open`, `IAsyncFile::sync`, and transaction range reads under a configurable prefix.

Control flow: Client 0 opens a locked unbuffered/uncached file, aligns a page buffer, reads all stored page ledger entries from `range`, validates on-disk pages against expected encoded values, then loops forever. Each loop chooses existing and appended pages, clears their ledger keys, increments a `syncs` metric key after the first cycle, commits, writes page buffers to disk, waits for writes, syncs, and commits new ledger entries.

State and persistence behavior: Persistent state is split between the file and FDB keys under `/DiskDurabilityTest/` by default. Clearing ledger entries before file writes models in-flight pages as unverifiable until sync and second commit complete.

Dependencies/integration: Uses Native API transactions, Flow file I/O, `fmt::print`, and tester single-client execution.

Risks: A crash between file sync and ledger commit leaves durable data untracked but safe; a crash after ledger commit with bad disk contents is detected next run. The unused read-version future hides latency but is not awaited. The loop has no duration timeout inside this file and relies on tester cancellation.

Test signals: `ValidationError` trace or thrown `operation_failed` on mismatch, `Verified` trace with page counts, and the `syncs` metric key.
