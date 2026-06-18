# Research: sources/user-network-fs/samba/source3/lib/netapi/serverinfo.c

Purpose: implements server information and remote time-of-day NetAPI functions over local Samba configuration and remote SRVSVC RPC. It translates `srvsvc_NetSrvInfo` levels into public `SERVER_INFO_*` buffers.

Important APIs/functions: local helpers `NetServerGetInfo_l_101` and `_1005` build server name/version/type/comment buffers from loadparm. `map_server_info_to_SERVER_INFO_buffer` maps SRVSVC levels 100, 101, 102, 402, 403, 502, 503, 599, and 1005, although the remote entry point only accepts a subset. `NetServerGetInfo_r`, `NetServerSetInfo_l`, `NetServerSetInfo_r`, `NetRemoteTOD_r`, and `NetRemoteTOD_l` are the exported request handlers.

Control flow: local get-info supports levels 101 and 1005 directly. Remote get-info validates level 100, 101, 102, 402, 502, 503, or 1005, obtains a SRVSVC binding, calls `dcerpc_srvsvc_NetSrvGetInfo`, and maps the returned union into a talloc-backed buffer. Local set-info only supports level 1005, validates the comment, requires the registry smb.conf backend, initializes an smbconf registry context, and writes global `server string`. Remote set-info supports level 1005 by passing a `srvsvc_NetSrvInfo1005` to `NetSrvSetInfo`. `NetRemoteTOD_r` calls `srvsvc_NetRemoteTOD` and duplicates the returned time structure.

State and persistence: remote get/time calls are read-only. `NetServerSetInfo_l_1005` persists the server comment in Samba's registry configuration backend. Remote set-info persists on the target server according to SRVSVC behavior. Output buffers are allocated under the NetAPI context.

Dependencies/integration: uses generated SRVSVC client stubs, Samba loadparm functions, SMB configuration registry APIs, and `libsmb/dsgetdcname.h`. It integrates with public `NetServerGetInfo`, `NetServerSetInfo`, and `NetRemoteTOD` wrappers and with the tests in `netserver.c`.

Risks: the map function includes code for levels not accepted by `NetServerGetInfo_r`, so future level enablement needs both validation and mapping reviewed. Several level 599 assignments contain comments such as `/* ?? */` and `/* typo ? */`, documenting uncertain field correspondence. Local set-info returns service-style errors for smbconf failures and calls `smbconf_shutdown(conf_ctx)` even after initialization failure paths, so `conf_ctx` lifetime assumptions matter. Tests include level 403 and tolerate status 124, reflecting partial implementation.

Test signals: integration tests should query levels 100, 101, 102, 402, 502, 503, and 1005, verify unsupported level behavior for 403/599 unless enabled, exercise remote TOD, and test local level 1005 with both registry and non-registry config backends.
