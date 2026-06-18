# sources/user-network-fs/s3fs-fuse/src/filetimes.h

## Purpose
Declares timestamp utilities and the `FileTimes` container used throughout s3fs-fuse for stat timestamp comparison, formatting, reflection, and update propagation.

## Important APIs, Types, And Functions
`enum class stat_time_type : uint8_t` identifies `ATIME`, `MTIME`, and `CTIME`. Free functions expose validation, comparison, stat-to-timespec conversion, timespec-to-stat conversion, stat time formatting, realtime acquisition, and realtime formatting. `FileTimes` owns `ft_ctime`, `ft_atime`, and `ft_mtime`; public helpers clear, get, reflect into `struct stat`, set individual times, set all times from now/stat/raw values/another `FileTimes`, and test omission.

## Control Flow
The class is a thin state container with inline typed wrappers delegating to private typed implementations in the `.cpp`. Construction initializes all fields to `UTIME_OMIT`. Public setters accept `timespec` by value so `SetTime()` can rewrite `UTIME_NOW` without mutating the caller's object. `SetAll()` defaults `no_omit` to true, so omitted source fields normally do not overwrite existing stored values.

## State And Persistence Behavior
`FileTimes` state is only the three `timespec` fields. There is no ownership of external resources, no dynamic allocation, no locking, and no disk persistence. The object is copyable by default because no special members are deleted; callers are responsible for synchronization when shared.

## Dependencies And Integration Points
The header depends on standard `cstdint`, `string`, and `sys/stat.h`. It is included by fd-cache and metadata conversion code, especially `fdcache_entity`, `fdcache_auto`, `fdcache`, `metaheader`, and `s3fs.cpp`. It bridges FUSE/system timestamp semantics with S3 metadata values.

## Risks
The API includes both reference-returning getters and copy getters; references are safe only as long as the `FileTimes` object remains alive and unmodified. The default `no_omit=true` behavior in `SetAll()` can be misread, so tests should document whether omitted source values are preserved or skipped. `ctime` is treated as a settable timestamp even though POSIX ctime is normally kernel-managed, which is appropriate for object metadata but can differ from local filesystem expectations.

## Test Signals
Header-level tests should compile across C++ standards and target platforms, assert initial omission for all fields, verify each inline wrapper maps to the correct `stat_time_type`, and exercise copy behavior if `FileTimes` is passed by value in cache operations. Integration tests should use the public API rather than private helpers.
