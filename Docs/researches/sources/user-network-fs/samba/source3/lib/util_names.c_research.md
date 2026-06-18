<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_names.c -->
# sources/user-network-fs/samba/source3/lib/util_names.c

## Purpose
`util_names.c` chooses Samba's default account domain/name context and enforces allowed-domain policy.

## Important APIs, types, and functions
Public APIs are `get_global_sam_name`, `my_sam_name`, and `is_allowed_domain`.

## Control flow
`get_global_sam_name` returns workgroup for a DC and NetBIOS name otherwise. `my_sam_name` returns NetBIOS name in standalone role and workgroup otherwise. `is_allowed_domain` first rejects domains matching `winbind:ignore domains`, then allows all trusted domains when configured, or only the local workgroup and local NetBIOS names when trusted domains are disabled.

## State and persistence behavior
No state is stored. Results reflect current loadparm configuration.

## Dependencies and integration points
It depends on server role macros, loadparm workgroup/netbios/trusted-domain settings, wildcard matching, and `is_myname`. It is used by authentication, winbind, and account resolution code.

## Risks and edge cases
Ignored-domain patterns take precedence over trusted-domain allowance. `is_myname` includes aliases and NetBIOS-length comparison semantics from `util.c`.

## Test signals
Tests should cover DC/standalone/member return values, ignored-domain pattern matching, trusted-domain allow-all mode, and local workgroup/name fallback mode.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_names.c -->
