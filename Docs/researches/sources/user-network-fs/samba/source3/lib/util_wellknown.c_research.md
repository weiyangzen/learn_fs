# sources/user-network-fs/samba/source3/lib/util_wellknown.c

## Purpose
`util_wellknown.c` maps a fixed subset of Windows well-known SID domains and RIDs to human-readable names and maps those names back to SIDs.

## Important APIs and Data
Static maps define `rid_name_map` entries for World/Everyone, Local Authority, Creator Owner, and NT Authority. `special_domains` ties those maps to global SID constants and domain display names. Public functions are `sid_check_is_wellknown_domain`, `sid_check_is_in_wellknown_domain`, `lookup_wellknown_sid`, and `lookup_wellknown_name`.

## Control Flow and State
The file is stateless and table-driven. SID lookup strips a RID, finds the matching special domain, then scans known users for the RID. Name lookup optionally filters by supplied domain and scans each table for a case-insensitive name match before composing the output SID and returning the canonical domain string.

## Dependencies and Integration Points
It depends on SID operations, talloc string allocation, and Samba string comparisons. It integrates with account lookup paths, ACL display, and LSA-style name/SID translation for built-in well-known identities.

## Risks and Test Signals
The maps are intentionally partial; unmapped well-known RIDs return false. `lookup_wellknown_name` reads `*pdomain` and assumes it is non-null. Tests should cover exact domain detection, SID-with-RID detection, known and unknown RIDs, empty-domain name lookup, domain-qualified lookup, case-insensitive names, and talloc allocation failures where injectable.
