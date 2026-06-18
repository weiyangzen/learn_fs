# File Research: sources/os/linux/linux/io_uring/cmd_net.c

## Purpose
Implements socket-specific `io_uring_cmd` operations for socket ioctls, sockopts, TX timestamps, and getsockname/getpeername-style queries.

## Main Functions
- `io_uring_cmd_get_sock_ioctl()`: calls protocol `ioctl` for `SIOCINQ`/`SIOCOUTQ`.
- `io_uring_cmd_getsockopt()`: supports `SOL_SOCKET` getsockopt and returns resulting optlen.
- `io_uring_cmd_setsockopt()`: calls socket setsockopt with userspace optval.
- `io_uring_cmd_timestamp()`: multishot timestamp command using the socket error queue and 32-byte CQEs.
- `io_process_timestamp_skb()`: extracts TX timestamp data and posts CQE32 multishot completions.
- `io_uring_cmd_getsockname()`: validates SQE fields and calls `do_getsockname()` with peer selector.
- `io_uring_cmd_sock()`: dispatches socket uring command opcodes and exports the symbol.

## Important Design Points
- TX timestamp command requires CQE32 support and uses `IORING_CQE_F_MORE`, timestamp type flags, and hardware timestamp flag.
- Timestamp processing removes eligible SKBs from the socket error queue, posts completions, and splices unprocessed SKBs back.
- `getsockopt` only supports `SOL_SOCKET` here.
- Compat handling is taken from `issue_flags & IO_URING_F_COMPAT`.

## Cross-File Relationships
- Uses `uring_cmd.h` and io_uring command completion helpers.
- Exported as `io_uring_cmd_sock()` for socket file operations to call.
- Depends on networking socket helpers and timestamp/error-queue APIs.

## Risks / Review Notes
- TX timestamp path is multishot and returns `-EAGAIN` to stay armed.
- Unsupported socket command operations return `-EOPNOTSUPP`, not generic ioctl fallback.
- `io_uring_cmd_getsockname()` rejects several SQE fields and allows `peer` only as 0 or 1.
