# sources/user-network-fs/samba/source4/librpc/idl/irpc.idl

## Purpose

`irpc.idl` defines Samba's internal RPC interface used between source4 services. It models management and notification calls for messaging servers, NBT, KDC checks, SMB server state, Samba termination, directory replication, DNS update, and DNS server reload.

## Important APIs And Types

The interface has UUID `e770c620-0b06-4b5e-8d87-a26e20f28340`, version 1.0, and imports misc, security, NBT, netlogon, and server-id IDL types. Public structs include `irpc_header`, `irpc_name_record`, and `irpc_name_records`. `irpc_header` carries interface UUID, version, call number/id, flags, NTSTATUS, a subcontext-wrapped credential token, and padding.

Management calls include `irpc_uptime`, `nbtd_information`, `nbtd_getdcname`, `nbtd_proxy_wins_challenge`, `nbtd_proxy_wins_release_demand`, `kdc_check_generic_kerberos`, `smbsrv_information`, `samba_terminate`, `dreplsrv_refresh`, `drepl_takeFSMORole`, `drepl_trigger_repl_secret`, `dnsupdate_RODC`, and `dnssrv_reload_dns_zones`.

Key discriminated types include `nbtd_info_level` and `nbtd_info` for NBT statistics, `smbsrv_info_level` and `smbsrv_info` for session/tree-connect listings, and `drepl_role_master` for FSMO role transfers.

## Control Flow And State

IDL does not implement behavior, but it defines request/response wire layout used by generated NDR parsers, clients, servers, and Python bindings. Many calls are administrative messages that trigger state changes in long-running daemons: terminating Samba, refreshing replication caches, taking FSMO roles, triggering secret replication, and reloading DNS zones.

## Dependencies And Integration Points

Generated output is built with `--header --ndr-parser --client --python` by the IDL `wscript_build`, making this interface available to C and Python users. It integrates with Samba's messaging/IRPC subsystem, NBT server, KDC/netlogon stack, SMB server management, drepl service, DNS update task, and internal DNS server.

## Risks

Internal RPC calls often cross daemon boundaries and may have privileged effects. Schema changes affect generated C and Python bindings and must preserve discriminant/value relationships. `irpc_header` embeds security tokens, so parser correctness and credential lifetime matter. Some calls accept strings or DNS name arrays from other components; malformed payloads should be rejected by generated NDR bounds and server-side validation.

## Test Signals

IDL generation should succeed for header, NDR parser, client, and Python outputs. Runtime signals include IRPC tests for uptime, NBT stats, SMB session/tcon reporting, DNS reload, and negative tests for invalid switch levels, malformed name arrays, and unauthorized administrative calls.
