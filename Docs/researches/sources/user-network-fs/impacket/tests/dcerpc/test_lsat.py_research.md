# sources/user-network-fs/impacket/tests/dcerpc/test_lsat.py

Purpose: tests LSA Translation (`lsat`) RPC name/SID lookup APIs over `\PIPE\lsarpc`.

Important APIs and functions: `LSATTests.open_policy()` uses `lsad.LsarOpenPolicy2` with lookup access. Tests cover raw/helper `LsarGetUserName`, `LsarLookupNames`, `LsarLookupNames2`, `LsarLookupNames3`, `LsarLookupNames4`, `LsarLookupSids`, `LsarLookupSids2`, and raw `LsarLookupSids3`.

Control flow: name tests build `RPC_UNICODE_STRING` values for Administrator and Guest, set lookup levels/options/client revision, and call raw/helper variants. SID tests first resolve Administrator to a domain SID, then build well-known RID suffixes such as `-500` and `-501`. Bulk SID lookup builds 1000 SIDs to force `STATUS_SOME_NOT_MAPPED`.

State and persistence behavior: read-only translation queries. No remote policy or account data is changed.

Dependencies and integration points: depends on `lsat` and `lsad` modules, LSA policy handle acquisition, domain-local Administrator/Guest names, and authentication. The v3/v4 tests assert access denial where Netlogon authentication would be required.

Risks: localized or renamed built-in accounts can change results. Expected denial strings for Netlogon-required paths can vary. Bulk 1000-SID test creates larger responses and may be slower on constrained domain controllers.

Test signals: verifies LSAT union formats, referenced domain handling, SID construction, helper/raw parity, access-control failures for v3/v4 APIs, and NDR64 behavior.
