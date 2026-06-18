# sources/user-network-fs/samba/source3/utils/net_rpc.c

## Purpose

`net_rpc.c` is the large RPC command implementation file for Samba's `net rpc` utility. It provides the top-level `net rpc` dispatcher and many of the concrete subcommands for managing Windows/Samba domains and servers over MSRPC/SMB. The file bridges command-line parsing in `utils/net.h` with Samba client subsystems such as SAMR, LSA, SRVSVC, NETLOGON, INITSHUTDOWN, WINREG, SPOOLSS, libnetapi, winbind, passdb, and secrets storage.

The command families implemented here include generic RPC setup and domain SID discovery, join/test-join and trust password changes, domain info/SID storage, user/group/share/file management, share and printer migration, share allowed-user analysis, shutdown, legacy trust-domain management, SAM vampire dispatch, and the final `net_rpc()` command table.

## Important APIs, Types, and Functions

`net_get_remote_domain_sid()` opens an unauthenticated LSA pipe, opens policy with maximum allowed access, queries `LSA_POLICY_INFO_ACCOUNT_DOMAIN`, and returns the remote account-domain name and SID. `run_rpc_command()` is the central wrapper: it optionally creates an IPC connection, allocates a temporary talloc context, gets the domain SID/name, opens the requested RPC pipe unless `NET_FLAGS_NO_PIPE` is set, invokes the callback, maps NTSTATUS success to shell status 0, and tears down pipe/connection/context. It handles NETLOGON schannel setup, sealed NTLMSSP pipes, TCP transport, and unauthenticated pipe opens.

Join and trust-password commands include `rpc_changetrustpw_internals()`, `net_rpc_changetrustpw()`, `net_rpc_oldjoin()`, `net_rpc_join_newstyle()`, `net_rpc_join()`, and `net_rpc_testjoin()`. These use `trust_pw_change()`, `libnet_Join`, DC discovery, and `libnet_join_ok()` to join or validate domain membership. `rpc_info_internals()` queries SAMR domain information, and `rpc_getsid_internals()` stores the domain SID with `secrets_store_domain_sid()`.

User commands are exposed by `net_rpc_user()`. Common operations use libnetapi calls such as `NetUserAdd`, `NetUserDel`, `NetUserSetInfo`, `NetGroupGetInfo`, `NetUserGetGroups`, and `NetQueryDisplayInformation`. Interactive shell helpers `net_rpc_user_cmds()` and `net_rpc_user_edit_cmds()` use direct SAMR calls to show or edit user fields and account flags through user info level 21.

Group commands are exposed by `net_rpc_group()`. Creation and rename use libnetapi. Deletion, membership changes, listing, and member enumeration use SAMR and LSA directly. `get_sid_from_name()` resolves names or textual SIDs. Domain groups and aliases are handled separately via `dcerpc_samr_OpenGroup()`/`OpenAlias()` and the corresponding group/alias member APIs.

Share and file commands are exposed by `net_rpc_share()` and `net_rpc_file()`. Share add/delete/list use `NetShareAdd`, `NetShareDel`, `NetShareEnum`, and SRVSVC helpers. `get_share_info()` fetches level 1, 2, or 502 share data. Migration functions copy share definitions, files, metadata, and security descriptors using SRVSVC plus SMB tree connections. File commands use `NetFileEnum()` and `NetFileClose()`.

The allowed-user feature uses `struct full_alias`, process-global `server_aliases`, `struct user_token`, winbind APIs, Samba `security_token` objects, and `se_access_check()` to estimate which local users can access remote shares. `net_usersidlist()` emits input for `net rpc share allowedusers`.

Shutdown commands use INITSHUTDOWN first and fall back to WINREG. Trust-domain commands create/delete interdomain trust accounts, establish/revoke trust passwords, list incoming/outgoing trusts, and vampire trust secrets using SAMR, LSA, passdb, and RPC session keys. Printer commands mainly dispatch to spoolss internals implemented elsewhere.

## Control Flow

Most commands enter through `net_rpc()`, are selected by `net_run_function()`, then either run a libnetapi operation directly or call `run_rpc_command()`. `run_rpc_command()` creates/reuses `cli_state`, discovers domain SID/name, opens the requested pipe, invokes the callback, and returns shell success/failure.

Exceptions include join/trust-establish flows, which need custom credential and DC discovery behavior; `rpc_share_allowedusers()`, which deliberately runs SAMR, LSA, then SRVSVC passes; shutdown fallback from INITSHUTDOWN to WINREG; and migration commands, which orchestrate several ordered RPC/SMB phases.

## State and Persistence Behavior

This file performs many persistent remote and local mutations. Joins can create/update machine accounts and possibly local registry-backed configuration. Trust password and SID operations update machine trust credentials, `secrets.tdb`, or passdb trusted-domain secrets. User, group, alias, share, open-file, printer, shutdown, and trust commands mutate remote servers. Share migration creates destination shares, copies file trees/metadata, and applies ACLs.

Transient memory usually lives under talloc contexts created by `run_rpc_command()` or local stackframes. `server_aliases` and `net_mode_share` are file-static process state used across helper calls. Some buffers use `SMB_MALLOC_ARRAY`, `SMB_STRDUP`, winbind allocation, and explicit free macros.

## Dependencies and Integration Points

The file depends on `utils/net.h`, source3 SMB client state, generated NDR clients for SAMR/LSA/NETLOGON/SRVSVC/SPOOLSS/INITSHUTDOWN/WINREG, libnetapi, winbind client APIs, passdb, secrets, loadparm, and Samba security descriptor helpers. It also dispatches to neighboring `net rpc` modules for audit, rights, service, registry, shell, trust, and conf commands, and to printer/vampire internals declared in shared headers.

## Risks and Edge Cases

Key risks include broad `MAXIMUM_ALLOWED_ACCESS` use, mixed NTSTATUS/WERROR/NET_API_STATUS/shell status conversion, LSA domain SID discovery as a prerequisite for many commands, fixed-size `fstring` path construction in recursive copy logic, static callback locals in `copy_fn()`, process-global alias state, and secret-handling paths that decrypt or persist trust passwords.

Specific suspicious areas include `rpc_user_password()` relying on `argv[1]` with only `argc >= 1`, `rpc_share_migrate_files_internals()` closing only final share connections after multi-share loops, `show_userlist()` querying a root security descriptor only when `cli_ntcreate()` is not OK, and `rpc_trustdom_del_internals()` assigning `result = status` after a failed delete result instead of propagating `result` into `status`.

## Test Signals

High-value tests include dispatch/usage tests, integration tests for `info`, `getsid`, `testjoin`, users, groups, shares, files, trusts, and printers, negative tests for permission denied and nonexistent objects, pagination tests for SAMR/NetAPI enumeration, migration tests for ACL/attribute/timestamp combinations and long paths, allowed-user tests with controlled SID files and aliases, and static analysis for buffer sizes, status conversion, cleanup, globals, and secret-handling code.
