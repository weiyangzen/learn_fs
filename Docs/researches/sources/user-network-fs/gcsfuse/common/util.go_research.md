<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/common/util.go -->
# Research: sources/user-network-fs/gcsfuse/common/util.go

Purpose: shared utility helpers for shutdown composition, Linux kernel-version probing, kernel-list-cache feature gating, and small file read/write helpers.

Important APIs/types/functions: `ShutdownFn`, `JoinShutdownFunc`, `GetKernelVersion`, `kernelVersionToTest`, `IsKLCacheEvictionUnSupported`, `CloseFile`, `WriteFile`, and `ReadFile`.

Control flow: `JoinShutdownFunc` runs non-nil shutdown callbacks in order and accumulates errors with `errors.Join`. Kernel detection shells out to `uname -r`, then regex-matches unsupported 6.9 through 6.12 kernel series. File helpers open paths, defer `CloseFile`, and use `WriteAt` or `os.ReadFile`.

State and persistence: `kernelVersionToTest` is a package variable deliberately replaceable in tests. `WriteFile` mutates an existing file from offset zero; it does not truncate trailing content. `CloseFile` calls `log.Fatalf` on close failure, which exits the process.

Dependencies: context, errors, regexp, `os/exec`, `os`, and process kernel reporting. Integration points include tests and features deciding whether kernel list cache eviction is supported.

Risks: hard-coded unsupported kernel regexes can age quickly. `WriteFile` requires an existing file and may leave stale bytes if new content is shorter. Fatal close behavior is harsh for library-style use. `GetKernelVersion` is Linux-specific.

Test signals: `util_test.go` mocks `kernelVersionToTest`, checks joined error contents, and validates temporary file read/write helpers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/common/util.go -->
