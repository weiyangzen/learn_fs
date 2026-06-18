# sources/user-network-fs/samba/source3/rpc_server/rpcd_epmapper.c

## Purpose
This daemon wrapper exposes the endpoint mapper service outside AD DC mode. It lets `samba-dcerpcd` provide epmapper as a small single-worker service.

## Important APIs, Types, And Functions
`epmapper_interfaces` returns `ndr_table_epmapper` except on AD DC, where source4 `samba` provides it. `epmapper_servers` registers supported default auth types with an empty principal, supplies `epmapper_get_ep_server`, and similarly disables the server list on AD DC. `main` runs one worker with a 10 second idle timeout.

## Control Flow
Both list and service callbacks branch on `lp_server_role`. Non-AD DC roles advertise and register epmapper; AD DC advertises zero interfaces and zero endpoint servers.

## State And Persistence
No direct persistent state is owned here. Auth type registrations modify the runtime dcesrv context.

## Dependencies And Integration Points
Dependencies include generated epmapper NDR, loadparm, role constants, and `rpc_worker_main`. The host uses its advertised bindings to populate `epmdb.tdb`.

## Risks And Test Signals
Risks include role mismatch between list and service mode, and auth type registration that diverges from what clients expect. Test signals are role-specific `--list-interfaces`, endpoint lookup through epmapper on fileserver/member roles, and absence of this service on AD DC.
