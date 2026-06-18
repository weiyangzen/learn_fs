# sources/storage-engines/tikv/components/txn_types/src/lib.rs

Purpose: public facade and error model for TiKV transaction types.

Important APIs/types/functions: re-exports lock, timestamp, key/value/mutation, and write types; defines `ErrorInner`, `Error`, `Result`, `maybe_clone`, `ErrorCodeExt`, and `ENABLE_DUP_KEY_DEBUG`.

Control flow: errors convert from I/O, codec, lock/write format, key lock, write conflict, and invalid operation variants. `ErrorCodeExt` maps each variant to storage error codes for downstream handling.

State and persistence: no persisted state, but error variants carry transaction keys, timestamps, lock info, and reasons across API boundaries.

Dependencies/integration: central import point for storage transaction code and clients needing typed transaction errors.

Risks: specialization-based generic `From<T>` requires nightly features; `maybe_clone` intentionally cannot clone I/O errors.

Test signals: no direct tests in this file; exported modules have focused tests.
