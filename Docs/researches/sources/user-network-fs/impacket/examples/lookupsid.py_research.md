# sources/user-network-fs/impacket/examples/lookupsid.py

## Purpose

`lookupsid.py` brute-forces RID values through LSARPC lookup calls to enumerate local or domain account names. It connects over SMB named pipe `\pipe\lsarpc` on port 139 or 445 and uses LSA policy information to derive the base SID.

## Important APIs, Types, and Functions

`LSALookupSid.KNOWN_PROTOCOLS` maps SMB ports to LSARPC string bindings. `__init__()` stores credentials, hashes, port, maximum RID, domain SID mode, and Kerberos flag. `dump(remoteName, remoteHost)` builds the DCE/RPC transport, applies remote host and credentials, and calls `__bruteForce()`. `__bruteForce()` connects, binds LSAT, opens a policy handle, queries the base SID, batches candidate SIDs, calls `hLsarLookupSids()`, and prints mapped names.

## Control Flow

The CLI parses target, optional max RID, connection port, `-domain-sids`, and authentication settings. `parse_target()` provides credentials and remote name; the script prompts for a password when needed and sets `target_ip` default. Batches of 1000 RIDs are generated from `0` through `maxRid`. `STATUS_NONE_MAPPED` skips a batch; `STATUS_SOME_NOT_MAPPED` still yields a packet with partial names; unknown SID uses are suppressed.

## State and Persistence Behavior

The script is read-only and writes only stdout/log output. It maintains local batch counters and DCE connection state, then disconnects after enumeration.

## Dependencies and Integration Points

It depends on Impacket DCE/RPC transport, LSAT/LSAD helpers, SAMR `SID_NAME_USE`, `MAXIMUM_ALLOWED`, and `DCERPCException`. It integrates with Windows LSA lookup policy and can use NTLM or Kerberos over SMB.

## Risks and Edge Cases

Large `maxRid` values generate many lookup requests and can be noisy. `SIMULTANEOUS=1000` may exceed limits if packet privacy or fragmentation settings are enabled, as comments note. `dump()` catches and re-raises, while the CLI catches all exceptions and suppresses them with `pass`, so failures may only be visible in logs. `entries` is unused. Domain SID mode may forward requests to a DC and behave differently from local account-domain enumeration.

## Test Signals

Tests should mock LSA responses for no mappings, partial mappings, full mappings, host SID versus domain SID selection, and port-specific transport settings. Integration tests should verify output against known local accounts and domain users, Kerberos authentication, redirected stdout encoding, and behavior for max RID boundaries.
