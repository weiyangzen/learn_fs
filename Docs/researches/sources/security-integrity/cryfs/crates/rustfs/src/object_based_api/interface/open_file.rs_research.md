# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/interface/open_file.rs

Purpose: object interface for an opened regular file.

Important APIs: `read`, `write`, `flush`, `fsync`, `getattr`, and `setattr`.

Control flow and state: adapters store open-file instances in `OpenFileList` keyed by `FileHandle`. `read` returns owned `Data`, then adapters pass a borrowed slice to callbacks. `write` receives `Data` and adapters report the input length as written after success.

Dependencies and integration: used by high and low-level adapters for handle-based I/O and metadata changes.

Risks and tests: open mode enforcement and short-write semantics are implementation-dependent. Returning the input length after `write` assumes success means all bytes were written.
