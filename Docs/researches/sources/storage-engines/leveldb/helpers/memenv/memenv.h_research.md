# sources/storage-engines/leveldb/helpers/memenv/memenv.h

Purpose: declares the helper API for creating an in-memory LevelDB environment.

Important APIs and types: forward declaration `Env` and exported `Env* NewMemEnv(Env* base_env)`.

Control flow: callers pass a live base env; the returned env delegates non-file-storage operations while overriding file APIs.

State and persistence behavior: data is memory-resident and tied to the returned env object's lifetime. The base env must remain live while the wrapper is in use.

Dependencies and integration: uses `LEVELDB_EXPORT` for shared-library visibility. Used by tests and clients that need a temporary DB without filesystem persistence.

Risks and edge cases: callers own the returned pointer and must delete it after all DB/file objects using it are closed.

Test signals: covered by `memenv_test.cc`.
