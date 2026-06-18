# sources/user-network-fs/samba/source3/rpc_server/rpcd_winreg.c

## Purpose
This daemon wrapper exposes the Windows registry RPC service for source3.

## Important APIs, Types, And Functions
`winreg_interfaces` returns `ndr_table_winreg`. `winreg_servers` returns `winreg_get_ep_server`, initializes the full registry stack with `registry_init_full`, loads share configuration, and returns one endpoint server. `main` uses five workers and a 60 second idle timeout.

## Control Flow
List mode always advertises winreg. Worker mode initializes registry state before endpoint registration and translates registry initialization errors from `WERROR` to `NTSTATUS`.

## State And Persistence
Registry initialization may open or prepare persistent registry databases. The wrapper itself only triggers initialization and share-load side effects.

## Dependencies And Integration Points
It depends on generated winreg NDR compatibility, the source3 registry initialization layer, loadparm shares, and `rpc_worker_main`. Many other RPC services may make local winreg calls, so availability affects broader RPC behavior.

## Risks And Test Signals
Risks include registry database initialization failure and service-to-service dependency failures when winreg is not available. Test signals are `--list-interfaces`, registry open/query/set RPCs, startup with corrupt/missing registry backend, and local winreg calls from other workers.
