# sources/security-integrity/selinux/libsepol/src/port_record.c

## Purpose
`port_record.c` implements opaque high-level `sepol_port_t` and `sepol_port_key_t` records for SELinux port-context mappings.

## Important APIs and State
`struct sepol_port` stores low/high port numbers, a libsepol protocol enum, and an owned `sepol_context_t *`. `struct sepol_port_key` stores the comparable range/protocol tuple. APIs create, unpack, extract, compare, clone, and free keys and records; get/set ranges and protocol; stringify protocols; and clone contexts into records.

## Control Flow and Integration
Setters mutate only the record. `sepol_port_set_con()` deep-clones the supplied context before replacement. `sepol_port_clone()` creates a new record and deep-clones the context if present. Comparators sort by low port, high port, and protocol. `ports.c` translates these records to and from `policydb->ocontexts[OCON_PORT]`.

## Risks and Test Signals
Range and protocol validation is limited here; low/high ordering is enforced in `ports.c`, and unknown protocols stringify as `"???"`. Tests should cover clone ownership, context replacement, comparator ordering, and invalid protocol/range behavior through the policydb wrapper.
