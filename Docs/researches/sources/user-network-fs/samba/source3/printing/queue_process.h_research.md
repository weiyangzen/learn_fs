# sources/user-network-fs/samba/source3/printing/queue_process.h

## Purpose

`queue_process.h` declares the public interface for the Samba source3 printing background queue process. It lets smbd initialize the printing subsystem, start the daemon, register daemon-side message handlers, and send messages to the daemon.

## Important APIs, Types, and Functions

- `printing_subsystem_init()` initializes background queue support and the print backend.
- `start_background_queue()` starts `samba-bgqd` and returns its PID.
- `send_to_bgqd()` sends a typed message buffer to the daemon.
- `struct bq_state` is an opaque daemon handler state.
- `register_printing_bq_handlers()` installs background queue daemon messaging and signal handlers.

## Control Flow

The header describes a split lifecycle: smbd calls `printing_subsystem_init()` before serving print workloads; that function can use `start_background_queue()`. The daemon process calls `register_printing_bq_handlers()` after creating messaging and event contexts. Regular code uses `send_to_bgqd()` to send queue-update or related messages.

## State and Persistence

No state is stored in the header. It exposes opaque state ownership through `struct bq_state *`, keeping implementation details in `queue_process.c`.

## Dependencies and Integration Points

The declarations depend on `tevent_context`, `messaging_context`, `dcesrv_context`, and PID types from surrounding Samba headers. They are consumed by print backend and daemon startup code.

## Risks and Edge Cases

The header’s API assumes callers have initialized Samba messaging and event contexts. Misordered startup can produce missing daemon state or failed message delivery.

## Test Signals

Compile-time coverage should ensure prototypes match `queue_process.c`; runtime tests should verify each exported function’s startup/send/registration path through smbd and `samba-bgqd`.
