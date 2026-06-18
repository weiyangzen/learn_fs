# sources/user-network-fs/samba/source4/dsdb/common/tests/dsdb_dn.c

## Purpose
`tests/dsdb_dn.c` is the local torture coverage for DSDB DN syntax parsing, formatting, canonicalization, comparison, and invalid input rejection for normal DNs, DN+Binary, and DN+String.

## Important APIs, Types, and Functions
- `torture_dsdb_dn_attrs()` tests LDB syntax handler comparison and canonicalization for `DSDB_SYNTAX_BINARY_DN` and `DSDB_SYNTAX_STRING_DN`.
- `torture_dsdb_dn_valid()` tests construction, parsing, linearization, extended linearization, casefolding, and extra-part lengths.
- `torture_dsdb_dn_invalid()` tests malformed normal, binary, string, extended, newline, and NUL-containing inputs.
- `torture_dsdb_dn()` registers the `dsdb.dn` suite with `valid`, `invalid`, and `attrs` tests.

## Control Flow
Each test initializes an LDB context, registers Samba handlers, and configures UTF-8 casefold functions. Attribute tests fetch the schema syntax by OID and call comparison/canonicalization functions directly. Valid tests build LDB DNs and `dsdb_dn` wrappers, then assert exact string forms. Invalid tests feed malformed `ldb_val` blobs to `dsdb_dn_parse()` and assert rejection, with one newline normal-DN case downgraded to a warning pending DEL DN understanding.

## State and Persistence
The tests use only in-memory LDB contexts and talloc allocations. No database is opened or modified.

## Dependencies and Integration Points
Dependencies include Samba LDB syntax handlers, wrap casefold functions, DSDB DN parser/formatter implementation, and torture assertion utilities. The tests are direct regression protection for `dsdb_dn.c` and schema syntax registration.

## Risks and Edge Cases
- The normal DN newline case is a warning rather than a hard failure, documenting an unresolved ambiguity.
- Tests assert exact string/casefold formatting, so intentional formatting changes require coordinated test updates.
- Invalid tests cover many prefix length/hex failures but not every possible malformed separator or integer overflow case.

## Test Signals
This is strong focused coverage for DN+Binary and DN+String behavior: case-insensitive binary hex, case-sensitive string prefix, case-insensitive DN postfix, zero-length binary prefix, invalid length mismatch, invalid hex, `0x` prefix rejection, extended DN rejection, and embedded NUL rejection.
