# sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsGPFile.hh

## Purpose
Defines the request object and callback contract for third-party file movement through `XrdSfsFileSystem::gpFile()`.

## Important APIs, Types, And Functions
- `XrdSfsGPFile` carries transfer options, source/destination, local CGI, checksum type/value, trace id, parallelism hints, and an implementation-private union `gpfInfo`/`gpfID`.
- Option bits include `replace`, `mkPath`, `keepErr`, `delegate`, `verCKS`, and `useTLS`.
- `Finished(int rc, const char *emsg)` completes and deletes the request object by contract.
- `Status(GPFState state, uint32_t cpct, uint64_t bytes)` reports progress in pending, transfer, or checksum-validation states.

## Control Flow
Callers fill the object and invoke `gpFile()` with get, put, or cancel. Implementations either accept the request and report progress asynchronously or fail synchronously. On final completion they must call `Finished()` and stop referencing the object.

## State And Persistence
The object is request-scoped and stores both immutable request fields and implementation-private state. Actual file persistence and transfer checkpoints are implementation-defined.

## Dependencies And Integration Points
Included by `XrdSfsInterface.hh`. Integrates with third-party copy support, checksum validation, TLS/delegation policy, and status callbacks to clients.

## Risks And Edge Cases
`Finished()` deletes the object by API contract, so use-after-finish is a primary risk. Cancel handling must coordinate with in-flight async transfers. Implementations must honor `keepErr`, `replace`, and checksum verification semantics to avoid data loss.

## Test Signals
Cover get/put/cancel, option bit combinations, progress callback cadence via `pingsec`, checksum validation success/failure, failure cleanup with `keepErr`, and object lifetime after `Finished()`.
