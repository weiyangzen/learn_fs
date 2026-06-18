# sources/user-network-fs/samba/source3/rpc_server/mdssvc/srv_mdssvc_nt.h

Purpose: declares mdssvc service lifecycle entry points for the RPC service layer.

Important APIs: `init_service_mdssvc(struct messaging_context *msg_ctx)` and `shutdown_service_mdssvc(void)` are declared for service registration/lifecycle integration. The implementation in this subset instead provides generated endpoint init/shutdown wrappers in `srv_mdssvc_nt.c`, so these declarations likely correspond to broader Samba service registration code.

Control flow and integration: consumers include this header when setting up the mdssvc RPC pipe. The message context parameter indicates initialization may need Samba messaging integration.

State and persistence: the header declares lifecycle hooks only; persistent state is in `mdssvc.c` (`mdssvc_ctx`) and per-policy `mds_ctx` objects.

Dependencies: forward use of `struct messaging_context`; actual definition comes from included Samba headers in consumers.

Risks: if declarations drift from generated/server registration symbols, build or link errors will expose it. The header contains no behavioral safeguards.

Test signals: build/link coverage of mdssvc service registration is the primary signal.
