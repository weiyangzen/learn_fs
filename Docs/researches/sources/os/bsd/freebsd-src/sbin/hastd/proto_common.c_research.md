# File Research: sources/os/bsd/freebsd-src/sbin/hastd/proto_common.c

Read completely: 231 lines.

This file provides shared socket send/receive helpers for protocol backends, including optional descriptor passing over UNIX-domain sockets.

Key responsibilities:
- Detects whether a socket is blocking.
- Sends file descriptors using `sendmsg()` and `SCM_RIGHTS`.
- Receives file descriptors using `recvmsg()` and validates the control message.
- Sends data in chunks up to `MAX_SEND_SIZE` with `MSG_NOSIGNAL`.
- Retries `ENOBUFS` send failures with increasing delays for up to about 11 seconds.
- Uses `shutdown()` with NULL data to declare one-way direction in socketpair-style channels.
- Receives data with `MSG_WAITALL` and translates blocking-socket `EAGAIN` to `ETIMEDOUT`.

Important interactions:
- Used by both TCP and socketpair protocol backends.
- Descriptor send/receive is required for passing established TCP connections between daemon parent and primary worker.

Reliability notes:
- Send loops handle partial writes.
- Receive relies on `MSG_WAITALL`; short positive reads are not separately checked in this wrapper.
- Descriptor passing assumes the underlying transport supports `SCM_RIGHTS`, so TCP backend asserts descriptor passing is not requested.
