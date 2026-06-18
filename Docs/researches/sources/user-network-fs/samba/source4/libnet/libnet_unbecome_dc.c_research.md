# sources/user-network-fs/samba/source4/libnet/libnet_unbecome_dc.c

## Purpose

`libnet_unbecome_dc.c` implements an asynchronous libnet workflow that demotes a Samba/AD domain controller back to a member-style computer account, modeled after Windows Server 2003 behavior. It discovers a source DC, modifies the destination computer account over LDAP, moves it to the Computers container, then removes the DS server/NTDS Settings objects through DRSUAPI.

## Important APIs, Types, and Functions

Public APIs are `libnet_UnbecomeDC_send()`, `libnet_UnbecomeDC_recv()`, and synchronous `libnet_UnbecomeDC()`.

Major stages:
- `unbecomeDC_send_cldap()` and `unbecomeDC_recv_cldap()` send netlogon pings to the source address and populate domain, source DSA, and destination site data.
- `unbecomeDC_ldap_connect()`, `_rootdse()`, `_computer_object()`, `_modify_computer()`, and `_move_computer()` bind LDAP, discover naming contexts, locate the DC computer account, replace `userAccountControl` with `UF_WORKSTATION_TRUST_ACCOUNT`, and rename/move it under the well-known Computers container GUID.
- `unbecomeDC_drsuapi_connect_send/recv()`, `_bind_send/recv()`, and `_remove_ds_server_send/recv()` connect sealed DRSUAPI over TCP, bind with `DRSUAPI_DS_BIND_GUID`, parse remote bind-info variants, and call `DsRemoveDSServer` with commit enabled.

## Control Flow

The send function copies inputs into a composite state, constructs destination DNS name as lowercase NetBIOS plus domain DNS name, then starts CLDAP. CLDAP success drives a synchronous LDAP block; LDAP success starts DRSUAPI connect, bind, and server-removal tevent requests. Any failed stage sets composite status and stops; final DRSUAPI success calls `composite_done()`.

## State and Persistence Behavior

Remote persistent changes are significant: the destination account's `userAccountControl` becomes workstation trust, the computer object may be moved/renamed into `CN=Computers`, and `DsRemoveDSServer` removes DS server/NTDS Settings objects from the configuration partition. Local state is held entirely in the composite talloc tree. `recv()` currently zeroes `r->out` and returns status without carrying detailed error strings.

## Dependencies and Integration Points

Dependencies include CLDAP/netlogon ping, LDB/LDAP wrapper connections, DSDB utilities, well-known GUID DN syntax, DRSUAPI generated client stubs, DCERPC pipe connect, loadparm ping protocol, credentials, tsocket address parsing, and libnet composite infrastructure. `source4/torture/libnet/libnet_BecomeDC.c` uses this to clean up after a BecomeDC/vampire promotion test.

## Risks and Edge Cases

The workflow is destructive and must target the intended DC account. Search filters interpolate `dest_dsa.netbios_name` and rely on LDB formatting to avoid malformed filters. CLDAP timeout is short. LDAP steps are synchronous inside an async state machine, so they can block the event loop. `recv()` discards error detail. The code does not explicitly unbind DRS/LDAP; talloc cleanup owns resources. DRS bind-info parsing accepts several lengths but only stores a normalized `DsBindInfo28`.

## Test Signals

The BecomeDC torture test is the main integration signal. Additional tests should validate CLDAP-discovered fields, LDAP move idempotency when already in Computers, no-op account-control updates, DRS remove failure handling, wrong source/destination inputs, and preservation of useful error strings.
