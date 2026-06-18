# sources/object-store/rustfs/crates/ecstore/src/disk/error.rs

## Purpose
`error.rs` defines the disk-layer error taxonomy, result aliases, conversions to and from external error carriers, stable numeric codes for internode protobuf transport, equality/hash behavior, and a small bitrot/context wrapper surface. It is the central error contract for local disks, remote disks, erasure quorum reduction, metadata parsing, and store initialization.

## Important APIs, Types, And Functions
- `pub type Error = DiskError` and `pub type Result<T> = core::result::Result<T, Error>` establish the module-wide result shape.
- `DiskError` enumerates storage conditions such as format corruption, disk/volume/object absence, access denied, faulty disks, disk full, short writes, bitrot invalidity, quorum failures, source stalls, timeout, and invalid path.
- `DiskError::other` wraps arbitrary errors in `DiskError::Io(std::io::Error::other(...))`.
- `is_all_not_found`, `is_err_object_not_found`, and `is_err_version_not_found` classify common object-not-found cases.
- `is_retryable_internode_write_failure` and `internode_http_error_kind` downcast nested `InternodeHttpError` from an `Io` variant for retry/quorum metrics.
- `to_u32` and `from_u32` map variants to stable numeric codes for `rustfs_protos::proto_gen::node_service::Error`.
- `BitrotErrorType` and `FileAccessDeniedWithContext` provide additional wrapped error contexts.

## Control Flow
Conversions preserve disk errors when possible. `From<std::io::Error>` first attempts to downcast an `io::Error` containing a `DiskError`; if successful, it recovers the original variant, otherwise stores the original I/O error in `DiskError::Io`. The reverse conversion unwraps `DiskError::Io` or wraps non-I/O variants as `io::Error::other`, enabling a later downcast back to `DiskError`.

File metadata errors are mapped to disk-level object errors for not-found, version-not-found, corrupt, and method-not-allowed cases; other metadata errors become `Io`. Tonic statuses are converted into generic `Io` errors with the status message. Node-service protobuf errors use the numeric code; `Io` codes and unknown codes preserve `error_info` as a generic error.

Clone and equality are custom because `std::io::Error` is not cloneable or structurally comparable by default. Cloning an `Io` recreates an error with the same kind and message. Equality compares `Io` kind plus message, while non-I/O variants compare by numeric code. Hashing only hashes the numeric code, which means distinct `Io` messages hash the same even though equality can differ.

## State And Persistence Behavior
The enum itself is not persistent, but its `to_u32`/`from_u32` mapping is a wire-compatibility contract. Changing numeric assignments would break remote disk and node-service error interpretation. Error strings also propagate to logs, user messages, and protobuf `error_info`.

Because non-I/O `DiskError` values are embedded inside `io::Error::other`, the system can move disk errors through APIs that only accept `std::io::Error` and recover them later. That behavior is relied on by `error_conv.rs`, local filesystem wrappers, and tests.

## Dependencies And Integration Points
`rustfs_filemeta::Error` conversions connect metadata decode/read failures to disk errors. `rustfs_rio::{InternodeHttpError, InternodeHttpErrorKind}` integration enables retryable internode write detection and metric labels used by `error_reduce.rs` and erasure encode logic. Protobuf conversions integrate with `rpc/remote_disk.rs` and node service RPCs. `error_conv.rs` returns `std::io::Error` values that often contain `DiskError` instances and are later converted back into this enum.

Most ecstore modules depend on these variants directly: `disk/local.rs` maps filesystem failures, `disk_store.rs` emits `FaultyDisk` and `Timeout`, `store_init.rs` handles `UnformattedDisk`, `set_disk` read/write code reduces `ErasureReadQuorum` and `ErasureWriteQuorum`, and remote code distinguishes `FaultyRemoteDisk`.

## Risks And Edge Cases
- The `Hash` implementation for `Io` ignores the I/O error message while equality includes it. This is allowed only if equal values hash the same, but it can create many hash collisions for distinct I/O errors.
- `DiskError::from_u32(0x24)` creates an empty `Io` error; protobuf conversion treats incoming `Io` specially to preserve `error_info`, but direct `from_u32` callers receive little context.
- `is_all_not_found` returns false on any `None`, so callers must pass only concrete per-disk errors when checking complete not-found failure.
- `tonic::Status` conversion loses status code and structured metadata, keeping only the message.
- Adding a variant requires updating `Clone`, `to_u32`, `from_u32`, tests, and possibly conversion/reduction logic.

## Test Signals
Tests validate variant display and numeric round trips, `other`, I/O conversion and downcast recovery, not-found classifiers, equality/clone/hash behavior, JSON conversion, bitrot wrapping, access-denied context display, debug formatting, error source expectations, nested disk-error through `io::Error`, preservation of original I/O kind/message, and display preservation when converting to `io::Error`.
