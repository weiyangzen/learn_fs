<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/server_info_sam.c -->
# sources/user-network-fs/samba/source3/auth/server_info_sam.c

## Purpose
Builds `auth_serversupplied_info` from a passdb `struct samu` account for the source3 authentication stack. It bridges Samba's passdb identity data with the local UNIX account database and includes a special domain-controller guard for smbd/winbind recursion when the local machine account logs in.

## APIs, Types, and Functions
The exported entry point is `make_server_info_sam(TALLOC_CTX *mem_ctx, struct samu *sampass, struct auth_serversupplied_info **pserver_info)`. It allocates a base server-info object with `make_server_info()`, looks up the UNIX account with `Get_Pwnam_alloc()`, converts passdb data to a Netlogon `SamInfo3` using `samu_to_SamInfo3()`, fills `unix_name` and the `utok` UID/GID, and returns the result on the caller context. The only local helper, `is_our_machine_account()`, checks whether a username is exactly the configured NetBIOS name plus a trailing `$`.

## Control Flow, State, and Persistence
`make_server_info_sam()` works on a temporary talloc stackframe and moves only the completed `server_info` to the caller context. Failure paths return `NO_MEMORY`, `NO_SUCH_USER`, or the passdb conversion status after freeing temporary allocations. Persistent state is not written, but when running as a DC and authenticating the local machine account it calls `winbind_off()` for the process to avoid recursive smbd-to-winbind calls.

## Dependencies and Integration
The file depends on `auth.h`, `passdb.h`, loadparm helpers such as `lp_netbios_name()`, the passdb `struct samu` accessor set, NSS passwd lookup, and winbind client control. It is used by Kerberos session synthesis and passdb-backed NTLM authentication paths that need a source3 `auth_serversupplied_info`.

## Risks and Test Signals
Risks are mostly identity consistency issues: a passdb user without a local passwd entry fails authentication, `samu_to_SamInfo3()` errors propagate directly, and the machine-account winbind disable is global to the process. Test signals include passdb users with valid and missing UNIX accounts, machine account login on a DC, expected UID/GID in the local token, and correct domain/SID fields in generated `info3`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/server_info_sam.c -->
