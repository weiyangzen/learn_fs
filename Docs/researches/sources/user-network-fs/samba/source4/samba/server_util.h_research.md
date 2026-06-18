<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/server_util.h -->
# sources/user-network-fs/samba/source4/samba/server_util.h

## Purpose

This header exposes the server utility API for tevent trace state and callbacks.

## Important APIs, Types, and Functions

It forward-declares `struct samba_tevent_trace_state` and declares `create_samba_tevent_trace_state()` plus `samba_tevent_trace_callback()`.

## Control Flow

There is no runtime flow in the header. Consumers allocate state and pass the callback to tevent.

## State and Persistence Behavior

The header hides the internal state layout, preserving ABI flexibility for users that only hold an opaque pointer.

## Dependencies and Integration Points

It requires `TALLOC_CTX` and `enum tevent_trace_point` to be visible in including translation units. It is included by `server.c` and `process_prefork.c`.

## Risks and Edge Cases

The callback must receive state created by `create_samba_tevent_trace_state()`; passing another pointer will fail the `talloc_get_type_abort()` in the implementation.

## Test Signals

Compile tests should ensure both server and prefork code include the header cleanly. Runtime tests should confirm callback registration with tevent does not require knowledge of the state internals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/server_util.h -->
