# sources/user-network-fs/samba/source4/dsdb/common/dsdb_dn.h

## Purpose
`dsdb_dn.h` defines the `struct dsdb_dn` data container, DSDB DN syntax OID constants, and RMD flag constants used by DSDB link/DN handling code.

## Important APIs, Types, and Functions
- `struct dsdb_dn` contains the parsed underlying `ldb_dn`, the binary/string `extra_part`, the `dn_format`, and the source syntax `oid`.
- `DSDB_SYNTAX_BINARY_DN`, `DSDB_SYNTAX_STRING_DN`, `DSDB_SYNTAX_OR_NAME`, and `DSDB_SYNTAX_ACCESS_POINT` identify schema syntaxes.
- `DSDB_RMD_FLAG_DELETED` marks deleted linked-value metadata.
- `DSDB_RMD_FLAG_HIDDEN_BL` marks backlink values hidden because the backlink is not allowed by object class.

## Control Flow
The header has no executable flow. It defines the shared layout that `dsdb_dn.c`, schema handlers, and link-processing code use to interpret DN-valued attributes with optional metadata prefixes.

## State and Persistence
The struct represents parsed state from LDB attribute values. RMD flags correspond to metadata persisted in extended DN/link values elsewhere in DSDB.

## Dependencies and Integration Points
The type assumes `struct ldb_dn`, `DATA_BLOB`, and `enum dsdb_dn_format` are declared by including contexts. It is part of DSDB common infrastructure and supports DN parsing/canonicalization and linked-attribute handling.

## Risks and Edge Cases
- The header exposes raw fields, so callers can mutate parsed DN state directly; invariants rely on disciplined use of constructor/parser helpers.
- OID constants must remain aligned with schema syntax handling.

## Test Signals
Direct test signal comes through `dsdb_dn.c` tests that inspect `extra_part.length`, formatted output, and syntax-specific parsing behavior.
