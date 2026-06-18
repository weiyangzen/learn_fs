# sources/security-integrity/selinux/libsepol/src/port_internal.h

## Purpose
`port_internal.h` is an internal aggregation header for libsepol port record and port collection APIs.

## APIs and Integration
It includes `<sepol/port_record.h>` and `<sepol/ports.h>` behind `_SEPOL_PORT_INTERNAL_H_`. It defines no new functions or types. `port_record.c` and `ports.c` use it to share opaque `sepol_port_t` and `sepol_port_key_t` API declarations.

## Risks and Test Signals
The risk is mainly dependency hygiene because the header only reexports public declarations. Build coverage of port record and policydb port APIs validates it.
