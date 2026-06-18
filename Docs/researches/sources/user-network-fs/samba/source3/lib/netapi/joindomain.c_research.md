# sources/user-network-fs/samba/source3/lib/netapi/joindomain.c

## Purpose

`joindomain.c` implements machine domain join/unjoin, join-status discovery, joinable OU discovery, machine rename, and offline domain join provisioning/request/compose APIs. It was read as a complete 1,119-line file. The code bridges public NetSetup-style APIs to Samba's `libnet_Join`/`libnet_Unjoin`, wkssvc RPC, ADS LDAP helpers, secrets, DC locator, and ODJ NDR blob support.

## Important APIs, Types, and Functions

Key functions are `NetJoinDomain_l/_r`, `NetUnjoinDomain_l/_r`, `NetGetJoinInformation_l/_r`, `NetGetJoinableOUs_l/_r`, `NetRenameMachineInDomain_r/_l`, `NetProvisionComputerAccount_l/_r`, `NetRequestOfflineDomainJoin_l/_r`, and `NetComposeOfflineDomainJoin_l/_r`. Backend helpers are `NetProvisionComputerAccount_backend()`, `NetRequestOfflineDomainJoin_backend()`, and `NetComposeOfflineDomainJoin_backend()`. Remote wkssvc calls use `NetrJoinDomain2`, `NetrUnjoinDomain2`, `NetrGetJoinInformation`, `NetrGetJoinableOus2`, and `NetrRenameMachineInDomain2`; passwords are protected with `dcerpc_binding_handle_transport_session_key()` and `encode_wkssvc_join_password_buffer()`.

## Control Flow

Local join validates the domain, initializes `libnet_JoinCtx`, locates a writable DC when domain-join flags are set, builds explicit ADS credentials or uses context credentials, sets join flags, enables config modification/debug, and calls `libnet_Join`. Remote join opens a WKSSVC pipe, encodes the password with the RPC session key when present, raises the RPC timeout, and calls `NetrJoinDomain2`. Unjoin mirrors this pattern, with local unjoin first checking `secrets_fetch_domain_sid()` and resolving a DC when one is not supplied. ODJ provisioning builds a join context with `provision_computer_account_only`, composes `ODJ_PROVISION_DATA`, serializes it with NDR, and returns either base64 text or binary data. ODJ request decodes optional UTF-16LE base64 input, parses the ODJ blob, validates version and `NETSETUP_PROVISION_ONLINE_CALLER`, then performs an offline join and returns restart-required status.

## State and Persistence Behavior

Local join/unjoin and offline request mutate machine/domain state: Samba configuration, secrets databases, machine account credentials, and local join status through `libnet_Join` or `libnet_Unjoin`. Remote join/unjoin/rename mutate the target server through WKSSVC. Provision/compose APIs create transient serialized blobs but provisioning may create or reuse a domain computer account. Error strings are stored in the libnetapi context when lower layers provide details.

## Dependencies and Integration Points

Dependencies include ADS support, `libcli_auth`, generated wkssvc and ODJ NDR, `libnet_join`, `libnet_join_offline`, secrets, `dsgetdcname`, base64 utilities, domain SID helpers, and `netapi_private` RPC helpers. It integrates with public wrappers in `libnetapi.c`, context credentials from `netapi.c`, and Samba's server role/configuration state.

## Risks and Edge Cases

This is security-sensitive code because it handles administrative credentials, machine passwords, and offline join blobs. Remote passwords depend on a valid RPC session key. Local unjoin refuses when no stored domain SID exists. ODJ request accepts both raw base64 bytes and UTF-16LE BOM input but requires blob version 1 and the online-caller option. Several remote ODJ APIs deliberately return `WERR_NOT_SUPPORTED`; public wrappers call local implementations for provision/request/compose. Multi-step join/provision operations can leave external domain or local machine state changed if later serialization or configuration steps fail.

## Test Signals

Test signals include local and remote join/unjoin against AD test domains, bad credential handling, no-domain-SID unjoin, writable DC discovery failure, wkssvc timeout restoration, encrypted-password remote calls, joinable OU LDAP paths with and without `HAVE_ADS`, ODJ binary/text round trips, UTF-16LE ODJ input, unsupported remote ODJ functions, and restart-required return on successful offline request.
