## sources/storage-engines/rocksdb/env/composite_env_wrapper.h

### Purpose

`env/composite_env_wrapper.h` declares `CompositeEnv`, which delegates file operations to a `FileSystem` and time operations to a `SystemClock`, and `CompositeEnvWrapper`, which completes the `Env` interface by forwarding thread and process services to a target `Env`. It is the public internal bridge between the monolithic `Env` API and the split `Env`/`FileSystem`/`SystemClock` model.

### Important APIs, Types, And Functions

- `CompositeEnv` derives from `Env` and forwards DB path registration, file creation, directory/file metadata, locking, links, sync, option optimization, free-space checks, and clock methods to `file_system_` or `system_clock_`.
- `CompositeEnvWrapper` constructors accept raw or shared target envs plus optional file-system or clock overrides.
- `CompositeEnvWrapper::Name()` returns `CompositeEnv`; `IsInstanceOf()` recognizes that name and parent names.
- `Inner()` exposes the target env for customizable inspection.
- Threading methods such as `Schedule()`, `UnSchedule()`, `StartThread()`, `WaitForJoin()`, background-thread controls, IO/CPU priority controls, thread-list/status access, host name, dynamic-library load, and unique ID generation forward to `target_.env`.
- `PrepareOptions()` and `SerializeOptions()` are declared for implementation in `composite_env.cc`.

### Control Flow

Callers use `CompositeEnvWrapper` when they want target env thread services but a different filesystem or clock. File operations go through inherited `CompositeEnv` methods and eventually `file_system_`; thread/process operations go straight to the target env. Clock calls in `CompositeEnv` use `system_clock_`, so a wrapper can combine default threads, custom storage, and emulated time independently.

### State And Persistence Behavior

The header declares no persistence by itself. Runtime state consists of shared pointers held by `Env` for file system and clock plus `EnvWrapper::Target target_` for the forwarding env. File operations persist through the configured `FileSystem`; scheduling and background work persist only in target env runtime queues.

### Dependencies And Integration Points

It depends on `rocksdb/env.h`, `rocksdb/file_system.h`, and `rocksdb/system_clock.h`. It is used by `env.cc`, `composite_env.cc`, `env_chroot.cc`, and public helper APIs such as `NewCompositeEnv`. Windows macro undefines protect method names like `DeleteFile` and `GetCurrentTime`.

### Risks And Edge Cases

- The class assumes target env is prepared and non-null before forwarding; callers that bypass `PrepareOptions()` can dereference null target state.
- Splitting file and thread services means file-system implementations must be thread-safe under the target env's scheduling model.
- Method forwarding is broad and easy to miss when `Env` gains new virtual APIs; new APIs should be audited for whether they belong to file system, clock, or target env.
- `LoadLibrary` forwarding is unavailable on Windows and when dynamic extensions are disabled, so configurable plugin behavior can vary by build.

### Test Signals

Compile-time override coverage is important. Runtime tests should construct composite envs with default, memory, chroot, and custom FS implementations, then run basic file tests and background-thread scheduling tests. Static research only; no test command was run.
