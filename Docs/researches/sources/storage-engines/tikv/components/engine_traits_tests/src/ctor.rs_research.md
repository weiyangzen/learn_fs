# sources/storage-engines/tikv/components/engine_traits_tests/src/ctor.rs

Purpose: Tests generic engine construction behavior across basic, option-based, filesystem, and encryption rename cases.

Important APIs and control flow: Tests call `new_kv_engine` and `new_kv_engine_opt`, verify missing directories are created and writable, expect read-only directories to fail, and test encrypted DB reopen after directory rename by linking and deleting encryption metadata correctly. The renamed-dir test writes `foo=bar`, renames the DB directory, updates key-manager links, and verifies data at the new path.

State, persistence, and dependencies: Uses temporary directories, filesystem permissions, encryption key manager metadata, and persisted KV data.

Integration points, risks, and test signals: Validates constructor contracts used by all shared tests. Risks include missing directory creation, permission handling differences, CF option construction errors, and encryption metadata becoming path-stale after rename.
