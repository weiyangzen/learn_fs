# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/errno.h

## Role

`errno.h` defines the illumos system error number ABI. It is a public kernel/user header assigning stable integer values to traditional UNIX, System V, robust-lock, STREAMS, shared-library, filesystem, and networking errors.

## Error Ranges

- Core UNIX errors run from `EPERM` 1 through standard filesystem/process errors such as `ENOENT`, `EINTR`, `EIO`, `EBADF`, `EAGAIN`, `ENOMEM`, `EACCES`, `EINVAL`, `ENOSPC`, `EROFS`, and `EPIPE`.
- Adds math errors `EDOM`/`ERANGE`, System V IPC errors `ENOMSG`/`EIDRM`, channel/link/CSI errors, `EDEADLK`, `ENOLCK`, `ECANCELED`, and `ENOTSUP`.
- Defines filesystem quota error `EDQUOT`.
- Includes convergent and legacy errors such as `EBADE`, `EBADR`, `EXFULL`, `ENOANO`, `EBADRQC`, `EBADSLT`, and `EDEADLOCK`.
- Robust-lock errors include `EOWNERDEAD`, `ENOTRECOVERABLE`, and `ELOCKUNMAPPED`.
- STREAMS errors include `ENOSTR`, `ENODATA`, `ETIME`, and `ENOSR`.
- Shared-library and exec-related errors include `ELIBACC`, `ELIBBAD`, `ELIBSCN`, `ELIBMAX`, `ELIBEXEC`, `EILSEQ`, `ENOSYS`, `ELOOP`, `ERESTART`, `ESTRPIPE`, `ENOTEMPTY`, and `EUSERS`.
- BSD networking errors occupy the higher range, including socket type/address/protocol errors, network/connection errors, timeout/refusal/host errors, `EWOULDBLOCK` as `EAGAIN`, `EALREADY`, `EINPROGRESS`, and NFS `ESTALE`.

## Contract Notes

The numeric values are ABI. Consumers should treat aliases such as `EWOULDBLOCK` and historical duplicates such as `EDEADLK`/`EDEADLOCK` carefully, because applications and kernel compatibility code may depend on exact values.
