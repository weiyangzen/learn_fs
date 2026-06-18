# sources/user-network-fs/samba/source4/torture/rpc/samsync.c

## Purpose

This file implements the `torture_rpc_samsync()` Netlogon SAM database synchronization test. It creates BDC, workstation, and normal-user test accounts; opens Netlogon secure channels; runs `DatabaseSync`, `DatabaseDeltas`, and `DatabaseSync2`; decrypts returned deltas; and cross-checks those deltas against live SAMR, LSA, and SamLogon observations.

The test is a broad consistency harness for replication data, Netlogon credential chaining, SAMR object reads, LSA secrets/accounts/trusted domains, and encrypted secret handling.

## Important APIs, Types, and Functions

- `test_SamLogon()` builds NT/LM network responses from hashes and calls `netr_LogonSamLogon`, checking returned authenticators.
- `struct samsync_state` holds replication sequence numbers, domain names/SIDs, secure-channel creds, SAMR/LSA/Netlogon pipes, and lists of secrets/trusted domains discovered during sync.
- `samsync_open_domain()`, `samsync_query_samr_sec_desc()`, and `samsync_query_lsa_sec_desc()` provide cross-protocol lookup and security descriptor reads.
- `samsync_handle_domain()`, `policy()`, `user()`, `alias()`, `group()`, `secret()`, `trusted_domain()`, and `account()` validate individual `netr_DELTA_ENUM` payloads against SAMR, LSA, or SamLogon.
- `test_DatabaseSync()` performs full sync over domain, builtin, and privs databases and dispatches each delta to a handler after `samsync_fix_delta()`.
- `test_DatabaseDeltas()` requests deltas starting slightly before recorded sequence numbers.
- `test_DatabaseSync2()` repeats sync through the newer Netlogon operation.

## Control Flow

The top-level function creates a server-trust machine account (`samsynctest$`), workstation account (`samsynctest2$`), and normal user. It opens a SAMR pipe from the BDC join context, connects to SAMR, opens the workgroup domain, and changes OEM domain info to force a visible sequence update. It then opens LSA policy with maximum access.

Next it binds to Netlogon with `DCERPC_SCHANNEL | DCERPC_SIGN` as the BDC account and stores the resulting Netlogon credential state. It creates a second signed secure-channel Netlogon pipe as the workstation account for SamLogon validation. With both secure channels ready, it runs full sync, delta sync, and sync2. All paths end at a `failed:` label that leaves the created domain accounts and frees the top-level talloc context.

During `DatabaseSync`, each returned delta array is processed in a loop until no `STATUS_MORE_ENTRIES` remains. Delta payloads are decrypted/fixed with `samsync_fix_delta()`. Domain deltas cache names, SIDs, handles, sequence numbers, and compare domain info levels and security descriptors. User deltas open the user via SAMR, compare level 21 fields, compare group membership, parse optional private key material, and validate password hashes via workstation Netlogon SamLogon when possible. Secret deltas open the LSA secret, retrieve current/old values, decrypt them with the LSA transport session key, and compare data and mtimes.

## State and Persistence Behavior

This test intentionally mutates the domain. It creates three accounts and changes domain OEM information via `samr_SetDomainInfo` level 4. It records sync sequence numbers in memory and stores discovered secrets/trusted domains in talloc-owned linked lists. It does not write local files. Cleanup attempts to leave all created accounts even after failures, but the domain OEM info mutation is not restored.

## Dependencies and Integration Points

Dependencies include Netlogon, SAMR, LSA generated NDR bindings; secure-channel credential code; `libcli/samsync/samsync.h` for delta decryption; security descriptor comparison; MD4/SMBOWF crypto helpers; GnuTLS error mapping; and the torture join/account helpers. Integration is cross-protocol: Netlogon replication output is treated as source data, then checked against SAMR domain/user/group/alias reads, LSA secret/account/trusted-domain reads, and Netlogon SamLogon authentication.

## Risks and Edge Cases

The test is environment-sensitive and high impact: it needs privileges to create machine accounts, read secrets/privileges, open LSA objects, and perform BDC-style synchronization. Some checks accept Windows compatibility differences, such as unavailable trusted-domain level 8 info, access-denied LSA secrets, missing old secret values, or password-change timing ambiguity. The domain OEM info mutation is durable. A duplicated `NT_STATUS_NOLOGON_INTERDOMAIN_TRUST_ACCOUNT` branch in user logon handling is harmless but redundant.

Because it walks all sync deltas and may validate password material, failures can arise from policy, ACL, crypto negotiation, or timing rather than just code defects. Interrupted runs can leave test machine/user accounts. The test assumes domain data ordering supplies domain information before user/group/alias deltas for that database.

## Test Signals

Pass signals include valid Netlogon credential chaining on every sync call, decryptable deltas, matching SAMR/LSA security descriptors and object fields, successful or correctly rejected SamLogon attempts based on account flags, matching secret ciphertext-derived values after session-key decryption, and acceptable `DatabaseDeltas` results including `NT_STATUS_SYNCHRONIZATION_REQUIRED`. Failures indicate replication inconsistency, broken secure-channel crypto, incorrect SAMR/LSA object state, or insufficient test privileges.
