<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/encryption.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/encryption.rs

Purpose: adapts TiKV's data key manager to RocksDB's encrypted environment interface.

Important APIs/types/functions: `get_env`, `WrappedEncryptionKeyManager`, `EncryptionKeyManager` impl, `convert_file_encryption_info`, and `convert_encryption_method`.

Control flow: `get_env` returns the existing base environment when no key manager exists; otherwise it builds a key-managed encrypted RocksDB env around a provided or default base env. RocksDB calls are forwarded to `DataKeyManager` and converted into RocksDB encryption info.

State and persistence behavior: encryption metadata is managed by `DataKeyManager`; RocksDB file creation, lookup, deletion, and link operations route through this wrapper, affecting how SST/WAL files are encrypted on disk.

Dependencies/integration: used by crate-level `get_env` in `lib.rs`, then layered with file-system inspection. Depends on `encryption`, `kvproto::encryptionpb`, and `rocksdb::EncryptionKeyManager`.

Risks: conversion must stay exhaustive with protobuf and RocksDB method enums; file link/delete forwarding must match RocksDB lifecycle expectations or encrypted file metadata can leak or go stale.

Test signals: no direct tests in this file; exercised indirectly by env construction and encrypted RocksDB deployments.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/encryption.rs -->
