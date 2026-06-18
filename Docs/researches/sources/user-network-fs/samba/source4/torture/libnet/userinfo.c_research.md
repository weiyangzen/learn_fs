# sources/user-network-fs/samba/source4/torture/libnet/userinfo.c

## Purpose
`userinfo.c` tests the lower-level `libnet_rpc_userinfo` API, both synchronous and asynchronous, using SID and username inputs.

## Important APIs, types, and functions
`test_userinfo()` calls `libnet_rpc_userinfo` at level 5 by SID and by username. `test_userinfo_async()` calls `libnet_rpc_userinfo_send`/`recv` at level 10 and passes `msg_handler` for monitor messages. `torture_userinfo()` creates the domain/user setup and runs both modes.

## Control flow
The test connects to SAMR, opens the domain, creates `libnetuserinfotest`, derives the user SID by adding the created RID to the domain SID, and queries by SID then name. It deletes the user, repeats the setup, and exercises the async send/recv path.

## State and persistence behavior
The file creates and deletes a domain user twice. Runtime state includes SAMR handles, generated SIDs, composite async contexts, and monitor callbacks. Cleanup is explicit but can leave the test account if a failure occurs before delete.

## Dependencies and integration points
The file uses helpers from `utils.c`, generated SAMR stubs, `libcli/security` SID helpers, and `msg_handler()` for async monitor output. It is a lower-level complement to the high-level user API tests in `libnet_user.c`.

## Risks and edge cases
The SID path depends on correct RID return from SAMR create. Async testing requires the event context and composite context to be valid. The fixed username can collide with stale accounts from prior failed runs.

## Test signals
Passing tests confirm sync and async user-info calls work for SID-based and username-based lookup forms and that monitor callbacks do not break the async path.
