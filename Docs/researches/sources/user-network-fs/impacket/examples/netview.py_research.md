# sources/user-network-fs/impacket/examples/netview.py

## Purpose

`netview.py` continuously monitors SMB reachable domain machines for remote sessions and locally logged-in users. It can discover computers from SAMR, import target lists, filter reported users, and loop with a background aliveness checker so hosts that go down can be retried later.

## Important APIs, Types, and Functions

Global `machinesAliveQueue` and `machinesDownQueue` coordinate the aliveness thread with the polling loop. `checkMachines()` probes TCP/445, records the local source IP used for filtering self-sessions, and moves reachable machines into the alive queue. `USERENUM` owns credentials, target lists, filter users, live DCE handles, and connection budget.

`getDomainMachines()` binds to `\samr` with `transport.SMBTransport`, calls `hSamrEnumerateUsersInDomain` for `USER_WORKSTATION_TRUST_ACCOUNT`, and strips trailing `$` from machine accounts. `getSessions()` binds or reuses `\PIPE\srvsvc` and calls `srvs.hNetrSessionEnum` level 10. `getLoggedIn()` binds or reuses `\PIPE\wkssvc` and calls `wkst.hNetrWkstaUserEnum` level 1.

## Control Flow

Main parses an identity with `parse_identity`, initializes logging, builds `USERENUM`, and calls `run()`. `run()` resolves targets, builds optional user filters, starts `checkMachines()` unless `-noloop` is set, then repeatedly drains new alive machines into `self.__targets`. Each active target is polled for server sessions and local workstation users. On selected errors, targets are removed permanently or queued back as down; in single-pass mode, the loop exits after one scan.

Session tracking compares current RPC results with prior `Sessions` and `LoggedIn` collections. New entries produce “logged from host” or “logged in LOCALLY” messages; missing entries produce logoff messages. Filtering is applied only at reporting time, not collection time.

## State and Persistence Behavior

Local state is in-memory only: target dictionaries hold cached SRVS/WKST DCE objects, admin capability, prior sessions, and local logon sets. The script keeps remote RPC connections open until the `-max-connections` budget is exhausted, after which it disconnects new handles. No files are written except optional reads from user or target list inputs. Remote state is read-only.

## Dependencies and Integration Points

The script integrates with SAMR for domain machine discovery, SRVS for session enumeration, WKST for local user enumeration, `socket.create_connection` for liveness, and Impacket SMB/DCE transports for NTLM or Kerberos. It requires NetBIOS/FQDN resolution for domain machines and enough privileges for the SRVS/WKST calls, especially local logon enumeration.

## Risks and Edge Cases

`checkMachines()` mutates `deadMachines` while iterating over it, which can skip entries. The global `myIP` is set from the last successful probe and may not match all target paths on multi-homed hosts. In `getLoggedIn()`, `elif str(e).upper().find('ACCESS_DENIED'):` is truthy for `-1`, so many non-broken-pipe exceptions can be treated as access denied. Connection budget is shared but not locked. Removing list entries while enumerating previous sessions can skip adjacent removed sessions.

## Test Signals

Test with mocked queues and socket failures for aliveness transitions, SAMR pagination for machine discovery, SRVS/WKST mocked responses for login/logoff delta detection, filter file handling, single-pass termination, broken-pipe reconnection, and access-denied handling. A lab integration signal is stable reporting against a Windows host with remote SMB sessions and a non-admin account.
