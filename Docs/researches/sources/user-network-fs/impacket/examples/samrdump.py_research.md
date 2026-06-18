# sources/user-network-fs/impacket/examples/samrdump.py

## Purpose

`samrdump.py` enumerates users from a remote SAMR service and prints account metadata. It can emit human-readable output or CSV.

## Important APIs, Types, and Functions

`SAMRDump` stores auth settings, Kerberos options, SMB port, and CSV mode. `getUnixTime()` converts Windows FILETIME to Unix time. `dump()` prepares the `\pipe\samr` transport, fetches entries, converts password-last-set and account flags, and prints output. `__fetchList()` connects to SAMR, enumerates domains, opens the first domain, pages through users, opens each user, queries `UserAllInformation`, and closes user handles.

## Control Flow

The CLI parses target, CSV, auth, Kerberos/AES, DC IP, target IP, and SMB port. After password prompting and option normalization, `dump()` connects through `ncacn_np:<remote>[\pipe\samr]`, sets credentials and Kerberos, calls `__fetchList()`, then prints each returned `(username, rid, userInfo)` as CSV or key/value lines.

## State and Persistence Behavior

The script is read-only against SAMR and does not write files. It prints user metadata and can expose account status information. It opens and closes DCE/RPC and SAMR handles during enumeration.

## Dependencies and Integration Points

It uses Impacket `transport`, `samr`, `DCERPCException`, `STATUS_MORE_ENTRIES`, target parsing, and the example logger. It integrates with SMB named-pipe SAMR on Windows or compatible servers.

## Risks and Edge Cases

Only the first enumerated domain is queried. CSV output performs simple comma replacement on comments but does not quote fields, so embedded newlines or commas in other fields can still break CSV. `datetime.fromtimestamp()` uses local timezone. Exceptions during enumeration can skip disconnect because no `finally` wraps `dce.disconnect()`. Large domains can produce many per-user open/query calls.

## Test Signals

Mock SAMR tests should cover paged enumeration, `STATUS_MORE_ENTRIES` exception packets, FILETIME conversion, flag decoding, CSV formatting, and handle closing. Integration tests should include anonymous/low-privilege behavior, Kerberos/hash login, CSV mode, and a domain with enough users to require pagination.
