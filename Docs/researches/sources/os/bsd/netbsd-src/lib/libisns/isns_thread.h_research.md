# File Research: sources/os/bsd/netbsd-src/lib/libisns/isns_thread.h

Declares control-thread command ids, timer event ids, reconnect period, thread-name length, and the `isns_kevent_handler` function type. It exports the control thread entry point and handlers for pipe, socket, reconnect timer, and refresh timer events.

This header binds task/util code to the kqueue-based control loop.
