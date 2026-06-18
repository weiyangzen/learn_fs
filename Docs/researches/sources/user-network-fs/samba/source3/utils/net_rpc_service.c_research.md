# sources/user-network-fs/samba/source3/utils/net_rpc_service.c

## Purpose

`net_rpc_service.c` implements `net rpc service`, a Service Control Manager client for listing, querying, starting, stopping, pausing, resuming, creating, and deleting remote Win32 services over SVCCTL RPC.

## Important APIs, Types, and Functions

`struct svc_state_msg` and `state_msg_table` map SVCCTL state constants to localized display strings. `svc_status_string()` returns a talloc-backed state string. `open_scm()` wraps `OpenSCManagerW`; `open_service()` wraps `OpenServiceW`. `query_service_state()`, `watch_service_state()`, and `control_service()` provide common state query/control/poll behavior. Command internals implement list, status, stop, pause, resume, start, delete, and create. The exported `net_rpc_service()` registers these commands with `net_run_function()`.

## Control Flow

Each wrapper handles display-usage mode and then calls `run_rpc_command()` with `ndr_table_svcctl`. `list` opens SCM with enumerate rights, calls `EnumServicesStatusW` first with a zero-size buffer, reallocates on `WERR_MORE_DATA`, unmarshals the returned array with `ndr_pull_ENUM_SERVICE_STATUSW_array()`, and prints service/display names. `status` opens SCM and a service handle, queries current status, then queries configuration, retrying with the returned buffer size on `WERR_INSUFFICIENT_BUFFER`.

`stop`, `pause`, and `resume` share `control_service()`, which opens the service, sends the control code, polls for the desired final state, and prints the resulting state. `start` opens the service with start access, calls `StartServiceW`, polls for `SVCCTL_RUNNING`, and reports success or failure. `delete` opens with `SERVICE_ALL_ACCESS` and calls `DeleteService`; `create` opens SCM with create-service rights and calls `CreateServiceW` with a demand-start own-process service using the provided binary path.

## State and Persistence

Persistent state is remote SCM/service state: service runtime state, service records, and service configuration created or deleted by commands. The code does not persist local state. It keeps transient policy handles and NDR buffers under the per-command talloc context.

## Dependencies and Integration Points

The file depends on generated SVCCTL NDR/client stubs, common `net` RPC runners, and Samba string wrappers. It integrates as the `service` subtree under `net rpc` and uses `pipe_hnd->srv_name_slash` as the remote SCM server name.

## Risks

Several operations open SCM with `SC_RIGHT_MGR_ENUMERATE_SERVICE` even when subsequent service operations require service-specific rights; this may work because service rights are requested later, but can fail on stricter servers. `watch_service_state()` sleeps only `usleep(100)` per iteration and caps at 30 polls, making the total wait extremely short for real service transitions. Usage errors often return `NT_STATUS_OK`, which can make invalid invocations look successful to scripts. `list` manually unmarshals a buffer returned by the RPC stub, so changes in stub behavior could break parsing. Create uses fixed service type, start type, and no credentials/dependencies, limiting functionality.

## Test Signals

Tests should cover service listing with `WERR_MORE_DATA`, status config retry on insufficient buffer, start/stop/pause/resume state polling, create/delete of a disposable service, permission-denied propagation, invalid argument returns, and slow service transitions that exceed the current poll window.
