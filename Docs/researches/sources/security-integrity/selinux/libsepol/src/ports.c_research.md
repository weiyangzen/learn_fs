# sources/security-integrity/selinux/libsepol/src/ports.c

## Purpose
`ports.c` maps high-level `sepol_port_t` records to and from low-level SELinux `OCON_PORT` object contexts in a `policydb_t`.

## Important APIs and Control Flow
Internal helpers convert between libsepol protocol enums and `IPPROTO_*` values and between public records and `ocontext_t` objects. Public APIs count, test existence, query, modify, and iterate port mappings. Queries unpack a key, convert protocol, and linearly scan `policydb->ocontexts[OCON_PORT]`. `sepol_port_modify()` converts the record to a new object context and prepends it to the list.

## State, Persistence, and Integration
State lives in the in-memory policydb ocontext list and is persisted later by `write.c`. The runtime service `sepol_port_sid()` scans the same list to resolve SIDs for network ports.

## Risks and Test Signals
`sepol_port_modify()` does not replace existing entries, so duplicate keys are possible and first-match ordering matters. DCCP/SCTP constants are locally defined if absent. Tests should cover invalid protocols, low greater than high, query misses, callback early stop, and duplicate insertion ordering.
