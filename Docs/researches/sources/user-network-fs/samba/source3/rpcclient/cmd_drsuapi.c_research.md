# sources/user-network-fs/samba/source3/rpcclient/cmd_drsuapi.c

## Purpose
`cmd_drsuapi.c` adds `rpcclient` commands for Active Directory DRSUAPI operations: name cracking, domain-controller information queries, SPN writes, and replication change retrieval.

## Important APIs, types, and functions
- `cracknames()` builds a level-1 `DsCrackNames` request from caller-provided names and requested formats.
- `cmd_drsuapi_cracknames()` binds with `DRSUAPI_DS_BIND_GUID`, cracks one name to FQDN 1779 format, prints returned status/domain/result, and unbinds.
- `display_domain_controller_info_*()` helpers print info levels `01`, `1`, `2`, and `3`.
- `cmd_drsuapi_getdcinfo()` binds, sends `DsGetDomainControllerInfo`, and displays the returned level.
- `cmd_drsuapi_writeaccountspn()` parses `add`, `replace`, or `delete`, builds a `DsWriteAccountSpn` request, and sends it.
- `cmd_drsuapi_getncchanges()` negotiates bind extensions, resolves a default naming context when absent, chooses request level 8 or 5, calls `DsGetNCChanges` in a loop, and advances high-watermarks until `more_data` is false.

## Control flow
Every high-level command establishes a DRS bind handle and should unbind on exit. Name cracking and DC info are straightforward request/print flows. SPN writes validate the operation string and collect SPN names into an array before sending the request. `GetNCChanges` advertises many DRS extensions, inspects the server's returned extension set, derives a naming context via `cracknames()` when not supplied, obtains the binding auth session key, requests changes, handles compressed or uncompressed level-1/6 replies, and loops while the server reports more data.

## State and persistence behavior
Name cracking, DC info, and NC changes are read-only from the remote directory's perspective, although `GetNCChanges` can disclose replication data to authorized callers. `dswriteaccountspn` mutates the target AD object's service principal names. The client stores no persistent local state.

## Dependencies and integration points
The module depends on generated DRSUAPI client stubs, GUID helpers, DCE/RPC auth session key retrieval, Samba loadparm workgroup for default naming context resolution, and DRSUAPI replication structures.

## Risks and edge cases
- DRSUAPI operations are security-sensitive; `GetNCChanges` can expose directory secrets when run with sufficient replication privileges.
- Several early returns after a successful bind do not unbind, notably in default naming-context resolution failure paths.
- SPN writes can break service authentication if pointed at the wrong DN or operation.
- `GetNCChanges` has complex level/compression handling and must keep request level and high-watermark fields matched.

## Test signals
Test against a disposable AD DC: crack valid/invalid names, query DC info levels, add/replace/delete SPNs on a test object, and run `dsgetncchanges` with explicit and default naming contexts. Negative tests should cover insufficient privileges, unsupported extensions, and bad DNs.
