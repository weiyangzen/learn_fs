# sources/user-network-fs/samba/source3/rpc_server/rpc_worker.h

## Purpose
This header declares the generic `rpc_worker_main` entry point used by all source3 `rpcd_*` daemon wrappers.

## Important APIs, Types, And Functions
`rpc_worker_main` accepts argv, a daemon config name, default worker count and idle timeout, a `get_interfaces` callback returning NDR interface tables, a `get_servers` callback returning endpoint server implementations, and caller-private data.

## Control Flow
Concrete daemons implement two callbacks and return `rpc_worker_main(...)` from `main`. The generic worker owns option parsing, list mode, service initialization, messaging, endpoint registration, and event loop execution.

## State And Persistence
No state is declared by the header. Runtime state is allocated inside `rpc_worker.c` based on the provided callbacks.

## Dependencies And Integration Points
It includes `replace.h` and `dcesrv_core` so callers can name NDR interface and endpoint server types. It is included by every `rpcd_*.c` wrapper in this group.

## Risks And Test Signals
Risks are callback contract drift and mismatched daemon config names. Test signals are compile coverage for each daemon wrapper and `--list-interfaces` output matching `samba-dcerpcd` parser expectations.
