# sources/user-network-fs/samba/source3/rpc_server/svcctl/srv_svcctl_reg.h

Purpose: Header for SVCCTL registry initialization.

Important APIs: Declares `svcctl_init_winreg(struct messaging_context *msg_ctx)`, which ensures service keys exist in the registry before SVCCTL serves requests.

Control flow and state: No state in the header. The implementation uses the passed messaging context to open internal winreg handles and persist service metadata.

Dependencies and integration: Included by SVCCTL server startup code. Requires `messaging_context` type visibility from surrounding Samba includes.

Risks and test signals: A failed or missing declaration affects endpoint initialization. Build coverage and SVCCTL startup tests with winreg available/unavailable are sufficient signals.
