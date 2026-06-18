# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdXeqPgrw.cc

## Purpose

`sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdXeqPgrw.cc` implements page-level read and write requests with per-page checksums. These handlers support efficient verified transfer, retry of corrupted pages, asynchronous paged I/O, and close-time reporting of unresolved checksum errors. The source was read as a complete 639-line file.

## Important APIs, Types, and Functions

Constants derive protocol page/unit sizes and async thresholds: `pgPageSize`, `pgPageMask`, `pgUnitSize`, `pgAioMin`, and `pgAioHalf`. Protocol methods are `do_PgClose()`, `do_PgRead()`, `do_PgRIO()`, `do_PgWrite()`, `do_PgWAIO()`, `do_PgWIO()`, `do_PgWIO(bool)`, `do_PgWIORetry()`, and `do_PgWIOSetup()`. The code uses `XrdOucPgrwUtils` for checksum count, verification, and segment geometry; `XrdXrootdPgrwAio` for async; `XrdXrootdPgwCtl` for frame parsing and response construction; and `XrdXrootdPgwFob` for bad-offset tracking.

## Control Flow

Paged read unmarshals offset and length, rejects nonpositive lengths, gets the file handle, decodes optional path and retry flags, updates stats and monitoring, tries async when eligible, optionally offloads to a bound stream, then calls `do_PgRIO()`. `do_PgRIO()` chooses a page-multiple quantum bounded by iovec and buffer limits, reads data plus checksums from `XrdSfsFile::pgRead()`, converts checksums to network order, sends partial-result frames with original offsets, and sends an empty final result if EOF or zero bytes ended after partial framing.

Paged write validates that payload includes at least one checksum, validates path IDs enough to know whether stream draining is possible, allocates a per-file `XrdXrootdPgwFob`, updates stats/monitoring, offloads if requested, and enters `do_PgWIO()`. The write I/O path optionally uses async, validates retry size and bad-offset registration, sets up frame parsing with `XrdXrootdPgwCtl`, reads checksum/data frames from the socket, verifies checksums, records bad offsets, writes data through `XrdSfsFile::pgWrite()`, clears corrected retry offsets, advances frames, and returns bad-offset information. `do_PgClose()` checks the fob at close time and fails close if uncorrected checksum errors remain.

## State and Persistence Behavior

Paged write state is attached to the open `XrdXrootdFile`: `pgwFob` tracks checksum failures across writes until close, and `pgwCtl` is a protocol-level control object reused for frame parsing. Bad offsets persist for the open file lifetime and influence retry validation. File statistics record paged read/write operations and correction counts, but the actual file data and checksum persistence are delegated to the SFS implementation.

## Dependencies and Integration Points

The file depends on XrdSfs interfaces, platform iovec limits, XProtocol definitions, XrdBuffer, XrdLink, CRC/page utilities, XRootD AIO file objects, monitor/file stats, paged AIO, paged write control/fob classes, protocol state, trace macros, and the shared executor header. It integrates with the main close path, bound-stream offload, async I/O limits, per-file monitoring, checkpointed pgwrite execution, and SFS `pgRead`/`pgWrite` support.

## Risks and Edge Cases

Paged write protocol desynchronization is high risk because malformed frame setup can make it impossible to drain the socket reliably; the code intentionally closes the connection on those cases. Retry writes are constrained to one page, with unaligned offsets computed specially; off-by-one errors would either reject valid retries or allow cross-page correction. `do_PgClose()` converts outstanding checksum offsets into a close failure, so clients must handle write-success followed by close checksum failure. `do_PgRIO()` relies on page geometry and iovec calculations staying within stack array sizes. Async eligibility must avoid retry requests and respect per-link/server limits.

## Test Signals

Tests should cover aligned and unaligned pgread, EOF and short final results, retry-flag pgread, async and synchronous paths, bound stream offload, invalid/zero lengths, invalid handles, checksum conversion, pgwrite with valid frames, checksum failures producing bad-offset responses, too many bad offsets, retry writes for registered and unregistered offsets, retry crossing a page boundary, malformed frame setup causing connection error, SFS pgWrite failures requiring drain, checkpointed pgwrite, and close with zero, corrected, and uncorrected checksum errors.
