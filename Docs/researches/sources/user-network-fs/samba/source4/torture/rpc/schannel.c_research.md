# sources/user-network-fs/samba/source4/torture/rpc/schannel.c

## Purpose

This file contains secure-channel torture tests for Netlogon, SAMR, and LSA RPC. It verifies that workstation and server-trust machine accounts can establish Schannel-protected connections with sign/seal and different crypto modes, that credential chaining survives secondary connections and fresh sockets, that SamLogonEx validation keys decrypt correctly, that anonymous password-set attempts fail, and that multiple Schannel connections can operate concurrently.

## Important APIs, Types, and Functions

- `test_netlogon_ex_ops()` builds NTLM network logon responses for the command-line user, calls `netr_LogonSamLogonEx` at validation levels 6, 2, and 3, decrypts encrypted validation keys with `netlogon_creds_decrypt_samlogon_validation()`, and compares them with level 6 when available.
- `test_netlogon_ex_bug14932()` is a regression variant using a fixed NTLMv2 timestamp/names blob pattern associated with Samba bug 14932.
- `test_samr_ops()` performs SAMR connect/open and repeated `GetDomPwInfo` calls over a Schannel binding.
- `test_lsa_ops()` calls `lsa_GetUserName` and checks whether Schannel maps to anonymous or to explicit credentials, with Samba3 tolerance.
- `test_schannel()` is the main scenario for one machine account and one Schannel flag combination.
- `test_schannel_anonymous_setPassword()` attempts `ServerPasswordSet` or `ServerPasswordSet2` with anonymous credentials and requires a non-OK operation result.
- `torture_rpc_schannel()`, `torture_rpc_schannel_anon_setpw()`, `torture_rpc_schannel2()`, and `torture_rpc_schannel_bench1()` are externally registered torture entry points.
- `struct torture_schannel_bench` and `struct torture_schannel_bench_conn` hold benchmark state for async `LogonSamLogonEx` loops.

## Control Flow

`torture_rpc_schannel()` loops through workstation and server-trust account types and Schannel modes: auto, 128-bit, AES, and Kerberos variants, each with sign or seal. For each case, `test_schannel()` joins a machine account, parses the configured binding, sets Schannel flags, connects to SAMR, runs SAMR operations, maps the binding to Netlogon, and creates a secondary authenticated Netlogon connection. It checks capabilities, ordinary Netlogon operations, SamLogonEx, and the bug 14932 regression. It then switches transports for LSA operations: named pipe for policy-style LSA, TCP for LookupSids3-style behavior, then restores the original transport.

The same test drops sockets and reconnects to verify that Schannel credentials remain usable across fresh SAMR and Netlogon connections without an explicit new ServerAuthenticate. It then deliberately disables Schannel flags for one Netlogon connection: SamLogonEx must fail as unsafe, while traditional Netlogon operations without a new ServerAuth are still expected to work. Finally it leaves the joined domain.

`torture_rpc_schannel2()` opens two Schannel Netlogon pipes from shallow-copied credentials with independent netlogon credential state cleared, then alternates SamLogonEx calls on both pipes. `torture_rpc_schannel_bench1()` creates one or two workstation joins, opens configurable parallel Schannel Netlogon connections, changes one workstation password after connections are established, verifies new credentials can connect, and runs asynchronous SamLogonEx loops until a time limit expires.

## State and Persistence Behavior

The tests create and delete machine accounts based on `TEST_MACHINE_NAME` plus suffixes. The benchmark changes a workstation account password and updates local credentials. Runtime state includes Schannel credential chains stored in `cli_credentials`, per-pipe Netlogon credential state, async request counters, and temporary NTLM response buffers. No local files are persisted.

Cleanup uses `torture_leave_domain()` for successful paths. Some assertion failures can bypass cleanup in the immediate function scope, relying on the broader torture framework to unwind talloc state and cleanup join contexts.

## Dependencies and Integration Points

The file depends on generated Netlogon, LSA, and SAMR NDR clients; credential and Kerberos helpers; Schannel auth helpers; Netlogon operation helpers from the broader `netlogon.c` torture code; LSA lookup helpers; endpoint mapper and DCERPC binding APIs; and tevent async request handling. It integrates deeply with Samba's machine-account join helpers and with the active test domain's Schannel policy.

## Risks and Edge Cases

These tests are highly policy-sensitive. Kerberos Schannel is skipped for `ncalrpc` and NT4-style domains without a realm. Some LSA identity expectations differ when Schannel maps to anonymous and when testing Samba3. Validation level 6 is only compared when privacy makes it available; otherwise key comparison is skipped.

The benchmark has code risks: `extra_user2` is parsed into `user1_creds` instead of `user2_creds`, and totals are accumulated after `s->conns` is freed, which is a use-after-free pattern. The main Schannel test also resets `tctx->last_result` after an intentional failure path, so later result handling depends on that manual cleanup. As with other domain-joining torture tests, interrupted runs can leave machine accounts or changed machine passwords.

## Test Signals

Pass signals include successful Schannel SAMR/LSA/Netlogon operations across all configured flag combinations, valid Netlogon credential chaining, matching decrypted SamLogonEx session keys between validation levels, expected failure for unsafe non-Schannel SamLogonEx, non-OK anonymous password-set results, independent operation of two Schannel pipes, and sustained async benchmark requests without request errors.
