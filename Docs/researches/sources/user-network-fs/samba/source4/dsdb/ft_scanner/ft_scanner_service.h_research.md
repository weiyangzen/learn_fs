# sources/user-network-fs/samba/source4/dsdb/ft_scanner/ft_scanner_service.h

## Purpose

`ft_scanner_service.h` defines the shared service state for Samba's forest trust scanner task. The structure is used by service initialization, periodic scheduling, and trust scanning code.

## Important APIs, Types, and Functions

- `struct ft_scanner_service` contains:
  - `task`: the owning `struct task_server`.
  - `startup_time`: timestamp captured at service creation.
  - `l_samdb`: local samdb connection used for PDC checks, TDO searches, and trust blob writes.
  - `periodic.interval`: regular scan interval in seconds.
  - `periodic.next_event`: timestamp of the currently scheduled event.
  - `periodic.te`: the active tevent timer.

There are no function declarations in this header beyond the type definition; function prototypes are supplied by the generated `ft_scanner_service_proto.h`.

## Control Flow

The header does not implement control flow, but its fields define the service lifecycle. `ft_scanner_service.c` allocates and initializes the structure, `ft_scanner_periodic.c` mutates `periodic` fields during timer scheduling, and `ft_scanner_tdos.c` uses `task`, `l_samdb`, and `periodic.interval` for asynchronous scan work and timeout calculation.

## State and Persistence Behavior

All state here is in-memory and tied to the task talloc lifetime. `l_samdb` is a live database connection, but the header itself does not define persisted attributes. The periodic fields are process-local scheduler state and are lost on restart.

## Dependencies and Integration Points

The type depends on Samba task server, timeval, LDB context, and tevent timer definitions from included compilation units. It is the shared contract among the ft_scanner service, scheduler, and TDO scanner.

## Risks

Because the structure is shared across asynchronous callbacks, lifetime must stay rooted under the task for the duration of outstanding timers and scan requests. Future fields that are mutated by callbacks should be considered single-event-loop state unless explicit locking is added. The spelling/comment typo "between to periodic runs" is harmless but indicates comments should not be treated as API.

## Test Signals

Compile-time integration is the main signal. Runtime tests should indirectly validate that `periodic.te` replacement, `l_samdb` availability, and task-private data casting remain consistent across service startup, timer callbacks, and scanner callbacks.
