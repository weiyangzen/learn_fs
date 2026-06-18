# sources/distributed-fs/xrootd/src/XrdCl/XrdClClassicCopyJob.cc

## Purpose

This file implements the non-third-party `ClassicCopyJob`, the core byte-stream copy engine behind `xrdcp` and `CopyProcess` when a normal client-mediated transfer is used. It copies from stdin, local files, remote XRootD files, metalinks, ZIP archive entries, dynamic-size sources, or extreme-copy replica sources into stdout, local/remote files, or ZIP archives. It also handles chunk parallelism, substream scaling, page read/write when available, checksum modes, POSC cleanup, continue mode, transfer rate throttling and threshold failover, extended attributes, ZIP CRC metadata, write recovery, and progress callbacks.

Most implementation types are local to the file. The exported class stays small while the file contains a source/destination abstraction layer and concrete implementations for each transfer shape.

## Important APIs, types, and functions

Local helpers `Source` and `Destination` define the transfer contract. A `Source` can initialize, report size, seek for continue mode, produce `PageInfo` chunks, return checksums/additional checksums, copy xattrs, and optionally try another server. A `Destination` can initialize, accept chunks, flush queued writes, finalize, report checksum and size, set xattrs, and expose write-recovery redirect metadata.

Source implementations include `StdInSource`, `XRootDSource`, `XRootDSourceZip`, `XRootDSourceDynamic`, and `XRootDSourceXCp`. `XRootDSource` performs asynchronous chunked reads, scales outstanding requests by connected data streams, can use `PgRead`, and updates local checksum helpers. `XRootDSourceZip` reads a file inside a ZIP archive and supports `zcrc32`. `XRootDSourceDynamic` reads until short read/EOF instead of trusting a fixed size. `XRootDSourceXCp` uses `XCpCtx` and replica lists for multi-source extreme copy.

Destination implementations include `StdOutDestination`, `XRootDDestination`, and `XRootDZipDestination`. `XRootDDestination` opens a local or remote `File`, queues asynchronous writes or `PgWrite`, handles write-recovery metadata through `WrtRecoveryRedir`, calculates local destination checksums, and optionally creates/removes a `CpTarget` symlink. `XRootDZipDestination` appends a file into a ZIP archive, tracks `zcrc32`, updates archive metadata, and closes the archive.

`ClassicCopyJob::Run(CopyProgressHandler*)` is the exported operation. It reads all job properties, validates incompatible options, constructs the proper source and destination, performs the chunk loop, flushes/finalizes, copies xattrs, validates size, computes/checks checksums, emits monitor checksum events, and stores results.

## Control flow

`Run` begins by loading property-list options such as `checkSumMode`, `checkSumType`, `parallelChunks`, `chunkSize`, `posc`, `force`, `dynamicSource`, `zipArchive`, `xcp`, `preserveXAttr`, `xrate`, `xrateThreshold`, `rmOnBadCksum`, `continue`, `cpTimeout`, `zipAppend`, `addcksums`, and `doServer`. It rejects `force + continue` and `(force|continue) + zipAppend`, enables POSC when remove-on-bad-checksum is requested, and resolves checksum type `auto` via `Utils::InferChecksumType`.

It then constructs the source based on `xcp`, ZIP, stdio, dynamic source, or ordinary XRootD/local source. After source initialization and size discovery, it constructs stdout, ZIP append, or XRootD destination. For regular file destinations it adds an `oss.asize` CGI hint when source size is known, applies flags, and initializes the destination.

The main loop calls `src->GetChunk(pageInfo)`, enforces `CPTimeout`, optionally sleeps to cap `xrate`, optionally triggers `TryOtherServer` when throughput falls below `xrateThreshold`, updates progress counters, sends the chunk to `dest->PutChunk`, and calls progress/cancel hooks. Destination write errors with `errRetry` populate `LastURL` and `WrtRecoveryRedir` so `CopyProcess` can retarget and rerun the job.

After EOF, it flushes outstanding writes, optionally copies extended attributes when both source and target support them, verifies the received byte count against known size, stores `size`, finalizes the destination, and performs checksum work. In `end2end` mode it obtains source and target checksums, lower-cases both strings, emits a monitor event, and fails with `errCheckSumError` on mismatch, optionally removing the target file.

## State and persistence behavior

The copy job stores no durable state outside the destination and result property list. In-flight state includes queued read/write `ChunkHandler` objects, heap-allocated buffers transferred through `PageInfo`, local checksum calculators, file/zip handles, retry metadata, and progress counters. Destination files are the durable side effect.

POSC behavior delegates to XRootD open flags for remote destinations and manually removes local destination files in destination destructors when the copy fails. `rmOnBadCksum` also removes the target after checksum mismatch. Continue mode starts the source at the current destination size and recomputes local checksums from scratch when needed.

## Dependencies and integration points

The file depends on `File`, `FileSystem`, `Monitor`, `Utils`, `CheckSumHelper`, `CheckSumManager`, `RedirectorRegistry`, `ZipArchive`, ZIP operations, `PostMaster`, `JobManager`, `XRootDTransport`, `XCpCtx`, POSIX I/O, semaphores, and the default environment.

It integrates with `CopyProcess` through property lists and retry result keys, with `xrdcp` through CLI-generated properties, with `TPFallBackCopyJob` as the fallback job, with monitor events for copy/checksum telemetry, with `RedirectorRegistry` for metalink metadata, with `DefaultEnv` for tuning variables, and with PostMaster data-stream callbacks for parallel reads.

## Risks and edge cases

Memory ownership is intricate: chunks allocate buffers with `new[]`, transfer them through `PageInfo`, and destinations delete them after write completion. Any early-return path must delete the buffer it owns; many paths do this manually. Asynchronous read/write queues rely on semaphores and cleanup loops, so deadlocks or leaks are possible if callbacks never arrive during shutdown.

The file mixes fixed-size, dynamic, ZIP, stdio, and xcp semantics. Continue mode is unsupported for stdin and xcp, incompatible with force, and requires checksum recomputation for local files. Size validation subtracts destination size in continue mode, so incorrect destination stat values can produce false success or false data errors.

Checksum behavior is broad and inconsistent in details: ZIP remote checksums only support selected modes, `additionalCkeckSum` is misspelled in result keys, additional checksum formatting differs by source type, and `GetRawCheckSum` depends on raw CRC layout. Calling `dest->Finalize()` again after checksum mismatch may double-close some destinations.

`xrateThreshold` failover assumes `TryOtherServer` is meaningful for the source. `XRootDSourceDynamic` and `XRootDSourceXCp` have different support levels. Write recovery depends on destination properties `WrtRecoveryRedir` and `LastURL`; missing or malformed metadata prevents retry. `XRootDZipDestination` notes that PgWriteV for ZIP append is not implemented.

## Test signals

No focused tests are in this work item. Strong integration tests would cover local-to-local, local-to-remote, remote-to-local, stdio, dynamic source, metalink, ZIP read, ZIP append, xcp, POSC cleanup, continue mode, write recovery retry, rate limiting, threshold source switch, xattr preservation, checksum modes including preset/auto/additional, bad checksum removal, cancellation, and cp timeout.
