# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ksocket.h

## Purpose
Defines the opaque kernel socket API, callback events, callback registration structure, socket operation wrappers, reference management, and direct receive callback support.

## Main Interfaces
- `ksocket_t`: opaque kernel socket handle.
- Callback flag bits:
  - `KSOCKET_CB_CONNECTED`
  - `KSOCKET_CB_CONNECTFAILED`
  - `KSOCKET_CB_DISCONNECTED`
  - `KSOCKET_CB_NEWDATA`
  - `KSOCKET_CB_NEWCONN`
  - `KSOCKET_CB_CANSEND`
  - `KSOCKET_CB_OOBDATA`
  - `KSOCKET_CB_CANTSENDMORE`
  - `KSOCKET_CB_CANTRECVMORE`
  - `KSOCKET_CB_ERROR`
- `ksocket_callback_event_t`: callback event enum.
- `ksocket_callback_t`, `ksocket_callbacks_t`: callback declarations and vector.
- Socket APIs:
  - `ksocket_socket()`, `ksocket_bind()`, `ksocket_listen()`, `ksocket_accept()`, `ksocket_connect()`
  - send/receive variants including `sendmsg`, `sendmblk`, `recvmsg`
  - socket option, name, ioctl, poll, shutdown, callback, close functions
  - `ksocket_hold()`, `ksocket_rele()`
- Direct receive:
  - `ksocket_krecv_f`
  - `ksocket_krecv_set()`
  - `ksocket_krecv_unblock()`

## Dependencies And Relationships
Avoids directly including STREAMS by forward-declaring `struct msgb`; it also forward-declares `struct nmsghdr`. All operations take credentials where required.

## Research Notes
The direct receive mode bypasses sockfs buffering: the callback must consume all delivered data and returns a boolean indicating whether lower layers may continue or must apply backpressure.
