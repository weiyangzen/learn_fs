# sources/security-integrity/audit-userspace/lib/optab.h

Purpose: operator lookup table mapping audit comparison constants to rule syntax symbols: `=`, `!=`, `>`, `>=`, `<`, `<=`, `&`, and `&=`.

Important APIs/types: expanded into generated lookup functions and exposed primarily through `audit_operator_to_symbol`; parsing in other libaudit code uses the same constants.

Control flow: static data only. Listing code calls the generated integer-to-string path when printing fields and comparisons.

State and persistence: none.

Dependencies and integration: included by `lookup_table.c`, `auditctl-listing.c` indirectly via libaudit lookup APIs, and `lookup_test.c`.

Risks and test signals: operator constants must match kernel/libaudit rule encoding. `lookup_test.c` checks integer-to-symbol output for every entry.
