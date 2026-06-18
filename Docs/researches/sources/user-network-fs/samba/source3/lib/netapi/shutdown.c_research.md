# Research: sources/user-network-fs/samba/source3/lib/netapi/shutdown.c

Purpose: implements NetAPI shutdown initiation and abort operations over the INITSHUTDOWN RPC interface. It provides remote handlers plus local wrappers that redirect to localhost.

Important APIs/functions: `NetShutdownInit_r` creates an `lsa_StringLarge` message and calls `dcerpc_initshutdown_Init` with timeout, force-applications, and reboot flags. `NetShutdownAbort_r` calls `dcerpc_initshutdown_Abort`. `NetShutdownInit_l` and `NetShutdownAbort_l` use `LIBNETAPI_REDIRECT_TO_LOCALHOST`.

Control flow: each remote handler obtains an INITSHUTDOWN binding through `libnetapi_get_binding_handle`, performs the RPC with `talloc_tos()` scratch memory, converts NTSTATUS transport failures to WERROR, and returns the server's WERROR. The server-name parameter passed inside the RPC is `NULL`; the binding target carries the actual server choice.

State and persistence: no local state is stored. Successful init changes remote machine state by scheduling shutdown/reboot; successful abort cancels a pending shutdown. These are privileged, user-visible, and potentially disruptive operations.

Dependencies/integration: uses generated INITSHUTDOWN client stubs, LSA string initialization helpers, public/private NetAPI headers, and libnetapi binding acquisition. Public `NetShutdownInit` and `NetShutdownAbort` wrappers dispatch into these handlers.

Risks: operations are destructive against real systems and require suitable privileges. There is no local validation of timeout, force, reboot, or message content beyond RPC marshalling. Passing `NULL` as the RPC server argument matches this interface but can surprise maintainers expecting `r->in.server_name` to be forwarded.

Test signals: tests should use a controlled Samba/Windows test target or mocked RPC binding to verify parameter marshalling, access-denied mapping, abort-without-pending behavior, local redirect, and NTSTATUS-to-WERROR conversion without actually shutting down developer hosts.
