<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/ipc.h -->
# sources/user-network-fs/ksmbd-tools/include/ipc.h

## Purpose

Declares the userspace side of the ksmbd generic-netlink IPC channel.

## Important APIs, Types, and Functions

Defines IPC message size/buffer constants, `struct ksmbd_ipc_msg`, payload macro `KSMBD_IPC_MSG_PAYLOAD`, allocation/free/send functions, event processing, and init/destroy lifecycle.

## Control Flow

mountd initializes netlink, sends startup config, waits for kernel events, wraps received payloads as `ksmbd_ipc_msg`, pushes them to worker handling, and sends responses back through `ipc_msg_send`.

## State and Persistence Behavior

IPC state is owned by mountd/ipc.c: a netlink socket and queued heap messages. Message payloads are size-limited to 16 KiB for kernel compatibility.

## Dependencies and Integration Points

Depends on `linux/ksmbd_server.h` ABI structures and mountd worker processing.

## Risks and Edge Cases

Message size limits and payload struct layout must match kernel expectations. Callers own allocated messages and must free after send or processing.

## Test Signals

Tests need netlink integration with a matching kernel module plus allocation boundary tests for oversize messages.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/ipc.h -->
