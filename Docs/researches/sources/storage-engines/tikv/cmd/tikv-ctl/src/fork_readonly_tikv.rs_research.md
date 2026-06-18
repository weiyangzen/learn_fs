# sources/storage-engines/tikv/cmd/tikv-ctl/src/fork_readonly_tikv.rs

## Purpose
`fork_readonly_tikv.rs` builds an "agent" data directory from an existing TiKV data directory for read-only reuse. It copies or symlinks snapshots, KV RocksDB files, and raft engine/raftdb files while avoiding files that can be modified or unsafe to share.

## Important APIs, Types, And Functions
- Constants `SYMLINK` and `COPY` define accepted reuse modes.
- `run(config, agent_dir, reuse_snaps, reuse_rocksdb_files)` is the entrypoint called by `tikv-ctl reuse-readonly-remains`.
- `dup_snaps`, `dup_kv_engine_files`, and `dup_raft_engine_files` build the target directory layout.
- `reuse_stuffs` filters and copies/symlinks selected files.
- `replace_symlink_with_copy` swaps selected symlinks with writable copies.
- `rocksdb_files_should_copy` selects the highest-numbered RocksDB WAL matching `^([0-9]+).log$`.
- Small filesystem wrappers format errors with source and destination paths.

## Control Flow
`run` first rejects encrypted data directories, creates the agent directory, then duplicates snapshots, KV engine files, and raft engine files. Snapshot duplication selects only `.meta` and `.sst`. KV RocksDB duplication copies everything except `LOCK`; if WALs are external, it additionally reuses the WAL directory. In symlink mode it replaces the last WAL symlink with a copy because that WAL is the file most likely to need local modification. Raft-engine duplication either uses `RaftEngine::fork` and makes copied files writable, or applies the same RocksDB/raftdb reuse rules when raft-engine is disabled.

## State And Persistence Behavior
This module creates filesystem state under `agent_dir`. In symlink mode most SST/manifest-like files remain shared with the source, while mutable tail WAL files are copied and made writable. It intentionally refuses encryption because linking or copying encrypted file sets without matching key manager behavior could produce unsafe or unreadable clones.

## Dependencies And Integration Points
It depends on `TikvConfig` path inference, `encryption_export::data_key_manager_from_config`, `raft_engine::Engine::fork`, `DefaultFileSystem`, `regex`, Unix symlink APIs, and `main.rs` validation that restricts storage engine and raft-engine recovery/recycle settings before calling `run`.

## Risks And Edge Cases
- The code assumes Unix symlink support.
- The destination directory must not already exist; `create_dir` fails if it does.
- `reuse_stuffs` canonicalizes source entries and unwraps UTF-8 file names; unusual non-UTF-8 filenames would panic.
- Only the last WAL is copied in symlink mode; correctness relies on RocksDB WAL immutability assumptions documented in comments.
- The printed error says `reuse_redonly_remains`, a typo, but the behavior is clear.

## Test Signals
Inline tests cover snapshot filename matching and last-WAL selection. Integration safety is mostly validated by `main.rs` preconditions and by operational use against real TiKV data directories.
