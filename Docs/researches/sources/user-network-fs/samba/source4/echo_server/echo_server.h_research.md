# sources/user-network-fs/samba/source4/echo_server/echo_server.h

## Purpose

`echo_server.h` is the small private header for the source4 echo service example. It declares the service state structure and fixed UDP service port.

## Important APIs, Types, and Functions

The header forward-declares `struct task_server`, defines `struct echo_server` with a single `struct task_server *task` member, and defines `ECHO_SERVICE_PORT` as `7`. It uses an include guard named `__ECHO_SERVER_H__`.

## Control Flow

There is no runtime control flow in the header. `echo_server.c` includes it so service callbacks can carry the owning Samba task through socket and packet-processing state.

## State and Persistence Behavior

`struct echo_server` holds only in-memory task ownership. The port macro fixes all listener creation to the standard echo service port; changing it changes runtime bind behavior wherever `echo_add_socket()` is called.

## Dependencies and Integration Points

The header couples the echo implementation to Samba's `task_server` type without including the full process model header. It is private to the echo server directory and participates in the `ECHO` module build.

## Risks and Edge Cases

Port 7 is a privileged, historically assigned echo port. The double-underscore include guard is reserved-style C naming, though common in older code. The minimal struct leaves future service state additions ABI-local to this module.

## Test Signals

Compile coverage of `echo_server.c` validates the header. Runtime echo service startup validates that the task pointer is initialized before event callbacks dereference it.
