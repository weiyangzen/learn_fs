# sources/storage-engines/tikv/components/txn_types/Cargo.toml

Purpose: Cargo manifest for the private `txn_types` crate.

Important APIs/types/functions: declares package metadata, runtime dependencies for encoding, protobufs, errors, hashing, logging, allocation, and TiKV utilities, plus test dependencies.

Control flow: build metadata only.

State and persistence: no runtime state; controls the transaction type crate’s compilation.

Dependencies/integration: this crate is shared by storage, MVCC, lock, and write paths.

Risks: codec and protobuf dependency changes can alter persistent lock/write wire compatibility.

Test signals: no manifest-local tests.
