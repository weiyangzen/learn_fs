## sources/user-network-fs/go-fuse/fuse/misc_test.go

Purpose: unit tests for error-to-FUSE-status conversion.

Important APIs/types/functions: `TestToStatus` passes nil, `syscall.Errno`, and wrapped/ordinary errors into `ToStatus`.

Control flow: table-style assertions check that known syscall errors map to matching status codes and unknown errors map to `EIO`.

State and persistence: no state.

Dependencies and integration: validates `misc.go`, which is used by all syscall-backed adapters.

Risks and test signals: protects errno compatibility; broad filesystem behavior depends on this conversion.
