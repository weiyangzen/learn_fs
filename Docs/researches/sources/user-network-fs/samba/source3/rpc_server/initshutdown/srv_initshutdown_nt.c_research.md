# sources/user-network-fs/samba/source3/rpc_server/initshutdown/srv_initshutdown_nt.c

Purpose: thin initshutdown RPC compatibility layer that delegates shutdown and abort requests to the winreg shutdown implementation.

Important APIs/types/functions: `_initshutdown_Init`, `_initshutdown_InitEx`, and `_initshutdown_Abort` translate initshutdown request structures into `winreg_InitiateSystemShutdownEx` or `winreg_AbortSystemShutdown`.

Control flow: `Init` copies hostname, message, timeout, force-apps, and reboot flags into a winreg shutdown-ex request with reason zero. `InitEx` does the same but preserves the caller-provided reason. `Abort` copies the server field into a winreg abort request. Each function immediately returns the delegated winreg result.

State/persistence behavior: this file holds no independent state. Any shutdown scheduling, cancellation, authorization, and side effects are owned by the winreg server routines it calls.

Dependencies/integration: includes generated initshutdown and winreg NDR headers plus winreg server compatibility declarations. It shares the active `pipes_struct` with delegated calls so auth, fault, and memory behavior come from the winreg implementation.

Risks/test signals: correctness depends on field-for-field thunking and preserving the reason only for `InitEx`. Tests should compare initshutdown and equivalent winreg behavior, including access denial, abort behavior, timeout/reboot flags, and generated boilerplate dispatch.
