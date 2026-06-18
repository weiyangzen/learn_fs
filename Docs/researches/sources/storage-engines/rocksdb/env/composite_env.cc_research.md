## sources/storage-engines/rocksdb/env/composite_env.cc

### Purpose

`env/composite_env.cc` implements the compatibility wrappers that expose new `FileSystem` objects through the older `Env` file API and make `CompositeEnvWrapper` configurable/serializable. It lets RocksDB combine one object for thread/OS services (`Env`), one for storage (`FileSystem`), and optionally one for time (`SystemClock`) while preserving the legacy `Env` call surface.

### Important APIs, Types, And Functions

- `CompositeSequentialFileWrapper`, `CompositeRandomAccessFileWrapper`, `CompositeWritableFileWrapper`, `CompositeRandomRWFileWrapper`, and `CompositeDirectoryWrapper` adapt `FS*` file classes back to legacy `Env` file classes.
- `CompositeEnv::NewSequentialFile()`, `NewRandomAccessFile()`, `NewWritableFile()`, `ReopenWritableFile()`, `ReuseWritableFile()`, `NewRandomRWFile()`, and `NewDirectory()` create FS objects through `file_system_` and wrap them.
- `NewCompositeEnv()` constructs a `CompositeEnvWrapper` using `Env::Default()` plus a supplied `FileSystem`.
- `CompositeEnvWrapper::PrepareOptions()` fills missing file system and system clock from the target env after preparing the target.
- `CompositeEnvWrapper::SerializeOptions()` and `EnvWrapper::SerializeOptions()` emit configurable target state when needed.
- Option maps `env_wrapper_type_info`, `composite_fs_wrapper_type_info`, and `composite_clock_wrapper_type_info` register target env, file system, and clock fields with the customizable options framework.

### Control Flow

Wrapper methods allocate a target FS file object, pass converted `FileOptions` and fresh `IOOptions`/`IODebugContext`, and only reset the legacy result pointer when the FS call succeeds. Multi-read conversion maps legacy `ReadRequest` arrays to `FSReadRequest` arrays, calls the target, then copies per-request results and statuses back.

`CompositeEnvWrapper` construction registers nested options. During `PrepareOptions()`, the target env is resolved from raw/shared/owned state; missing `file_system_` and `system_clock_` are inherited from the target env. Serialization starts with parent `Env` serialization, then includes `target=` only when the target is not null/default and the config is not shallow.

### State And Persistence Behavior

This file persists no external data. It owns adapter objects and `unique_ptr`-held file handles whose operations ultimately mutate the configured file system. Configuration state is serializable through RocksDB's customizable option strings, but target env serialization is suppressed or omitted for default/shallow cases.

### Dependencies And Integration Points

It depends on `env/composite_env_wrapper.h`, `rocksdb/file_system.h`, `rocksdb/system_clock.h`, `rocksdb/utilities/options_type.h`, and string helpers. It is used by `Env::CreateFromUri()` when a filesystem URI is supplied, by `NewCompositeEnv()`, by chroot env construction, and by users who configure remote/custom file systems without replacing all Env thread services.

### Risks And Edge Cases

- Adapter methods create default `IOOptions` and `IODebugContext`, so caller-provided IO activity context from newer APIs is not represented on the legacy side.
- `CompositeWritableFileWrapper::target()` exposes the underlying `unique_ptr`, which is powerful and can break wrapper invariants if misused.
- Serialization/equality depends on target `AreEquivalent()` behavior and custom object names; incomplete implementations can make option comparison noisy or wrong.
- If `PrepareOptions()` is skipped, `file_system_` or `system_clock_` can remain null depending on constructor usage.
- Status conversion is mostly direct, but per-request and aggregate multi-read statuses must both be interpreted by callers.

### Test Signals

Existing coverage should include env basic tests through custom `TEST_FS_URI`, option-string create/serialize/compare tests, and FS wrappers that exercise read, write, multi-read, sync, unique ID, directory fsync, direct IO alignment, and error propagation. Static research only; no test command was run.
