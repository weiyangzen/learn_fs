# sources/security-integrity/audit-userspace/auparse/accesstab.h

Purpose: Build-time table mapping `access(2)` mode bits to symbolic permission tests.

Important APIs, types, and functions: Contains `_S(0x1U, "X_OK")`, `_S(0x2U, "W_OK")`, and `_S(0x4U, "R_OK")`; the comment notes `F_OK` is handled in interpretation code rather than as a table row. Used by `gen_accesstabs_h` to create `accesstabs.h`.

Control flow: No runtime flow. The table is macro-expanded by the generator.

State and persistence: Static input data for a generated header.

Dependencies and integration points: Integrated into auparse's interpretation of access mode fields. Depends on generated table machinery in `../lib/gen_tables.c`.

Risks and edge cases: `F_OK` being special-cased means table users must preserve that separate logic. Missing future permission bits would affect display fidelity.

Test signals: Indirect through table generation and interpretation tests for access permission fields.
