# sources/user-network-fs/samba/source4/torture/libnet/userman.c

## Purpose
`userman.c` tests lower-level SAMR-backed libnet RPC helpers for user add, async user add, user delete, user modify, and user info comparison.

## Important APIs, types, and functions
The file wraps `libnet_rpc_useradd`, `libnet_rpc_useradd_send`/`recv`, `libnet_rpc_usermod`, `libnet_rpc_userdel`, and `libnet_rpc_userinfo`. `test_usermod()` builds randomized changes with explicit `USERMOD_FIELD_*` flags. `test_compare()` reads info level 21 and checks only fields that were requested to change.

## Control flow
`torture_useradd()` opens a domain, tests sync add and cleanup, reopens, tests async add, and cleans up again. `torture_userdel()` pre-creates a user through raw SAMR and deletes it through `libnet_rpc_userdel`. `torture_usermod()` creates a user, repeatedly applies increasingly many random changes, then compares the resulting SAMR info record against the requested modifications.

## State and persistence behavior
The tests create, delete, rename, and modify a domain user. The current username variable can change when the account-name field is modified, while cleanup still targets the original test RDN via helper logic. Failed cleanup can leave modified domain users behind.

## Dependencies and integration points
This file depends on `usertest.h`, shared libnet torture helpers, SAMR generated clients, `msg_handler` monitor output, and Samba time conversion helpers. It exercises lower-level RPC-oriented libnet APIs rather than the high-level domain-name wrappers.

## Risks and edge cases
Random field selection can skip duplicates through `continue_if_field_set`, making test coverage probabilistic for multi-change calls. Time field round trips can be fragile. Account rename requires later operations to follow the new name accurately.

## Test signals
Success indicates sync/async add, delete, modify, and info APIs work at the RPC helper level and that SAMR info level 21 reflects requested user modifications.
