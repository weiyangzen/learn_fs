# sources/security-integrity/selinux/libsepol/src/symtab.c

## Purpose
`symtab.c` wraps generic hashtable creation and destruction for policy symbol tables.

## Important APIs and Integration
`symtab_init()` creates a hashtable using a djb2-style XOR hash and `strcmp`, then sets `nprim` to zero. `symtab_destroy()` destroys the underlying hashtable. Policydb symbol tables for commons, classes, roles, types, users, booleans, sensitivities, and categories use this abstraction.

## Risks and Test Signals
The hash masks by `h->size - 1`, assuming power-of-two table sizes. Hash overflow is intentional and annotated for UBSAN. Destroy does not null the table pointer. Policy parsing, symbol lookup, policydb destruction, and UBSAN builds exercise this file.
