# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sockfilter.h

## Role

Defines the kernel socket filter API used to intercept and manipulate socket lifecycle, control, and data paths.

## Key Contents

Defines opaque `sof_handle_t`, filter callback return codes, notification events, and function pointer types for active/passive attach, detach, inbound/outbound data, bind, listen, accept, connect, shutdown, name lookup, socket options, ioctl, mblk property adjustment, and notification.

Groups callbacks in `sof_ops_t` and defines `SOF_VERSION`.

## Interfaces

Exports registration and control helpers: `sof_register`, `sof_unregister`, `sof_newconn_ready`, `sof_bypass`, cookie get/CAS, data injection in both directions, receive/send flow control toggles, and moving a new connection between filter handles.

## Design Notes

The API supports both automatic and programmatic filter attachment and permits filters to defer, detach, continue, stop successfully, or stop with selected errors.
