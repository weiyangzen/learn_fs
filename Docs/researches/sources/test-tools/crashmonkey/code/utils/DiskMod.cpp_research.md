# sources/test-tools/crashmonkey/code/utils/DiskMod.cpp

Purpose: serializes and deserializes logical filesystem mutations represented by `DiskMod`. It provides a compact big-endian binary format consumed by CrashMonkey components and tests.

Important APIs/types/functions: `DiskMod::Serialize`, `Deserialize`, `GetSerializeSize`, `SerializeHeader`, `SerializeChangeHeader`, `SerializeDataRange`, `SerializeDirectoryMod`, constructor, and `Reset`. It uses `htobe16/64`, `be16/64toh`, `shared_ptr<char>`, and enum values from `DiskMod.h`.

Control flow: serialization computes the entry size, writes size/type/options, optionally writes path and directory flag, then writes range metadata and data when applicable. Checkpoint and sync mods contain only headers; fsync/create/remove stop after change headers; fallocate and sync-file-range carry offset/length but no payload. Deserialization walks the same format, reconstructing path strings and optional data.

State/persistence behavior: the serialized buffer is an in-memory binary representation of logical operations, not direct disk persistence. Endianness is normalized for portable logs.

Dependencies/integration: used by `RecordCmFsOps::Serialize` and `DiskModTest.cpp`. Risks/test signals: `SerializeDirectoryMod` asserts unimplemented, `Deserialize` does not bounds-check malformed buffers, and remove mods are serialized like create/fsync but deserialization only early-returns for fsync/create, so remove handling deserves scrutiny.
