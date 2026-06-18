<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_sd.c -->
# sources/user-network-fs/samba/source3/lib/util_sd.c

## Purpose
`util_sd.c` converts security descriptors and ACEs between Samba security structures and human-readable text, with optional remote LSA SID/name lookup through an SMB client connection.

## Important APIs, types, and functions
Permission maps `special_values` and `standard_values` translate compact strings like `R`, `W`, `FULL`, and `CHANGE` to access masks. Public APIs include `SidToString`, `StringToSid`, `print_ace`, `parse_ace`, and `sec_desc_print`. Internal helpers `cli_lsa_lookup_sid` and `cli_lsa_lookup_name` temporarily connect to `IPC$` and use LSARPC for name/SID resolution. `print_ace_flags`, `parse_ace_flags`, and `print_acl_ctrl` handle ACE flags and descriptor control flags.

## Control flow
SID-to-string first emits numeric SID and, when allowed and a client is supplied, resolves the SID through LSARPC and formats `DOMAIN<separator>name`. String-to-SID accepts numeric SID text first, otherwise resolves through remote LSA. `print_ace` emits trustee, type, flags, and either standard permission name, compact special permission letters, or hex mask. `parse_ace` tokenizes `sid:type/flags/mask`, resolves trustee, parses type and flags, maps standard or compact permission strings, then initializes a security ACE. `sec_desc_print` prints revision, control bits, owner, group, and DACL ACEs.

## State and persistence behavior
Remote lookup temporarily changes the client tree connection to `IPC$`, then disconnects and restores the original tree/share. No descriptors are persisted.

## Dependencies and integration points
The file depends on SMB client state, LSARPC generated stubs, RPC pipe helpers, security descriptor/SID helpers, loadparm winbind separator, and standard FILE/SEC access constants. It is used by command-line tools and diagnostics that display or parse ACLs.

## Risks and edge cases
Tree connection restore is critical so callers do not lose their original share context. Parsing prints errors to stdout and returns false, which is suitable for tools but not quiet library callers. Only allowed/denied ACE types are accepted in numeric/hex type parsing. Control-bit string `SR` is reused by two meanings in the table, so display can be ambiguous.

## Test signals
Tests should cover numeric and remote SID lookup, ACE print/parse round trips for standard and special permissions, bad flags/masks, descriptor printing, and preservation of client tcon state after lookup failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_sd.c -->
