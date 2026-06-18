# Research: sources/object-store/minio-mc/cmd/pipe_supported.go

## sources/object-store/minio-mc/cmd/pipe_supported.go

Purpose: Linux-specific support for increasing pipe buffer size before streaming stdin in `mc pipe`.

Important APIs and functions: build tag `//go:build linux` selects this implementation. `pipeMaxSizeProcFile` points to `/proc/sys/fs/pipe-max-size`; `setPipeSize` calls `unix.FcntlInt` with `F_SETPIPE_SZ`; `getConfiguredMaxPipeSize` reads and parses the proc file; `increasePipeBufferSize` applies either the requested size or the system maximum.

Control flow: if desired size is zero or negative, it attempts to read the kernel-configured maximum and set that value, ignoring `setPipeSize` errors in that branch. Otherwise it sets the caller-provided size and returns errors.

State and persistence: changes the kernel pipe buffer size for the provided file descriptor only; no durable storage mutation.

Dependencies and integration: called by `pipe-main.go` before upload. Depends on `golang.org/x/sys/unix` and Linux procfs.

Risks and tests: when auto mode reads procfs successfully, `setPipeSize` errors are swallowed. Permissions and kernel limits can make explicit sizes fail. No tests cover this platform path.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/pipe_supported.go -->
