# sources/storage-engines/rocksdb/env/env_posix.cc

## Purpose

`env_posix.cc` provides the default non-Windows RocksDB `Env` implementation and default `SystemClock`. It binds the higher-level `Env` API to the default `FileSystem`, POSIX time, dynamic library loading, background thread pools, thread status tracking, hostname/thread-id helpers, and singleton lifetime handling.

## Important APIs, types, and functions

- `PosixDynamicLibrary` wraps a `dlopen()` handle and implements `DynamicLibrary::LoadSymbol()` using `dlsym()`.
- `PosixClock : public SystemClock` implements wall-clock, monotonic, CPU time, sleeping, current Unix time, and formatting.
- `PosixEnv : public CompositeEnv` is the default `Env`, built from `FileSystem::Default()` and `SystemClock::Default()`.
- `PosixEnv::LoadLibrary()` resolves shared-library names, adds platform extensions/prefixes, searches optional colon-separated paths, and returns `PosixDynamicLibrary`.
- `Schedule()`, `UnSchedule()`, `SetBackgroundThreads()`, `IncBackgroundThreadsIfNeeded()`, `ReserveThreads()`, `ReleaseThreads()`, and priority-lowering methods delegate to per-priority `ThreadPoolImpl` instances.
- `StartThread()` creates a raw pthread for one-off tasks and records it for `WaitForJoin()`/shutdown joining.
- `Env::Default()` initializes supporting singletons and returns the static default `PosixEnv`.
- `SystemClock::Default()` returns the static default `PosixClock`.

## Control flow

`Env::Default()` first initializes `ThreadLocalPtr`, `CompressionContextCache`, and sync-point singletons. It then creates a static `PosixEnv` with `STATIC_AVOID_DESTRUCTION` and a static `JoinThreadsOnExit` object that joins raw started threads and thread-pool workers during process shutdown. `PosixEnv` construction initializes a mutex, allocates one `ThreadPoolImpl` for each `Env::Priority`, sets each pool's priority, installs this env as host env, and creates a `ThreadStatusUpdater`.

Background work is scheduled by priority into `thread_pools_[pri]`; queue length, unscheduling, reservation, release, and priority changes are direct `ThreadPoolImpl` operations. `StartThread()` allocates a small state object, starts a pthread that invokes the user function and deletes the state, then records the pthread id under `mu_`. `WaitForJoin()` joins all recorded ids and clears the list.

Dynamic library loading normalizes a requested name: empty name loads the current process, otherwise the platform extension is appended if missing and `lib` is prepended for Unix bare names. If a search path is supplied, each path component is tried as `path/libname`; otherwise `dlopen()` uses the system search path.

`PosixClock` chooses platform-specific APIs for nanosecond and CPU timing: `clock_gettime()` on Linux/BSD/AIX, `gethrtime()` on Solaris, Mach clock APIs on macOS, and `std::chrono::steady_clock` elsewhere.

## State and persistence behavior

`PosixEnv` owns process-lifetime thread pools, a mutex, a vector of joinable pthreads, and `allow_non_owner_access_`. No database data is persisted by this file directly; persistence is delegated to `FileSystem::Default()` through the `CompositeEnv` base. State that affects OS behavior includes background thread counts, reserved worker counts, lower CPU/I/O priority settings, and file access permissions indirectly consumed by POSIX file creation code outside this file.

The singleton lifetime is intentionally unusual: thread status updater is not explicitly deleted to avoid use-after-free during static destruction, and `STATIC_AVOID_DESTRUCTION` keeps the default env available late in process shutdown.

## Dependencies and integration points

The implementation is compiled only when `!OS_WIN`. It depends on POSIX headers (`pthread`, `unistd`, `fcntl`, `dlfcn`, `sys/time`, etc.), optional `liburing` headers, RocksDB `CompositeEnv`, `io_posix`, `ThreadPoolImpl`, `ThreadStatusUpdater`, `CompressionContextCache`, `ThreadLocalPtr`, and sync-point infrastructure. It integrates with `file_system.cc` via `FileSystem::Default()` and with broad tests in `env_test.cc` for thread pools, library loading, default env creation, static destruction, direct/chroot environment parameterization, and CPU priority behavior.

## Risks and edge cases

- `WaitForJoin()` iterates and clears `threads_to_join_` without locking, while `StartThread()` mutates it under `mu_`. It is safe under expected test/application sequencing but not a general concurrent join API.
- `JoinThreadsOnExit` intentionally leaks/avoids deleting the thread status updater. That trades memory cleanup for shutdown safety.
- Dynamic loading error paths depend on `dlerror()` state and platform library naming; path search is simple and does not escape or sanitize components.
- `GetThreadID()` falls back to copying `pthread_t` bytes into a `uint64_t` where `gettid()` is unavailable. This is practical but platform-shape dependent.
- `TimeToString()` returns a fixed-size string buffer that may include trailing NUL bytes because it resizes to `maxsize`.
- On non-Linux platforms, CPU priority and I/O priority hooks either degrade or no-op.

## Test signals

`env_test.cc` exercises `RunEventually`, `StartThread`, `TwoPools`, `DecreaseNumBgThreads`, `ReserveThreads`, `UnSchedule`, `LowerThreadPoolCpuPriority`, dynamic library loading with and without search paths, `MultipleCompositeEnv`, `CreateDefaultEnv`, `StaticDestruction`, and many default-env file operations. Parameterized tests run many cases against both `Env::Default()` and a `ChrootEnv`, with direct I/O enabled and disabled where supported.
