# sources/security-integrity/selinux/libsepol/src/policydb_validate.h

## Purpose
This internal header exposes policydb validation entrypoints to other libsepol compilation units.

## APIs and Integration
It declares `value_isvalid(uint32_t value, uint32_t nprim)` for generic one-based symbol value checks and `policydb_validate(sepol_handle_t *handle, const policydb_t *p)` for full policydb integrity validation. It includes `<stdint.h>`, `<sepol/handle.h>`, and `<sepol/policydb/policydb.h>`.

## Risks and Test Signals
The viewed file has no include guard, but duplicate declarations are benign in C. Compile coverage verifies the header, while semantic coverage comes through callers that invoke `policydb_validate()`.
