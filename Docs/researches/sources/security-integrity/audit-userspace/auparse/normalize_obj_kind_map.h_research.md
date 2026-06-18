<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/normalize_obj_kind_map.h -->
# sources/security-integrity/audit-userspace/auparse/normalize_obj_kind_map.h

## Purpose
Maps internal normalized object-kind constants to public object-kind strings.

## Important APIs, types, and functions
The `_S` entries cover unknown, filesystem objects, sockets, process/process-group, firewall, service, account, user session, VM, printer, system, audit config/rule, security policy/modules, memory, device, software, and integrity policy.

## Control flow
Generated `normalize_obj_kind_map_i2s` is returned by `auparse_normalize_object_kind`.

## State and persistence behavior
Static map data only.

## Dependencies and integration points
Depends on `normalize-internal.h` values assigned by `normalize.c`.

## Risks and test signals
Risks are missing mappings and semantically misleading labels for broad classes like `unknown` or `system`. Tests should assert object-kind strings for file, socket, account, service, and process events.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/normalize_obj_kind_map.h -->
