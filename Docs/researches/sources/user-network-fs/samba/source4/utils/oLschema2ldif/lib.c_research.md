<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/utils/oLschema2ldif/lib.c -->
# sources/user-network-fs/samba/source4/utils/oLschema2ldif/lib.c

## Purpose

This file implements the core `oLschema2ldif` converter. It reads OpenLDAP schema definitions, parses `attributetype` and `objectclass` records, and emits AD/LDB-compatible LDIF messages with schema attributes such as `attributeID`, `governsID`, `schemaIdGuid`, `attributeSyntax`, `oMSyntax`, `mustContain`, `mayContain`, and class category fields.

## Important APIs, Types, and Functions

- `check_braces()` detects complete schema records and malformed final closing braces.
- `skip_spaces()`, `add_multi_string()`, and `get_def_value()` support token parsing.
- `get_next_schema_token()` recognizes OpenLDAP schema keywords (`NAME`, `SUP`, `MUST`, `MAY`, `SYNTAX`, `DESC`, etc.) and returns `struct schema_token`.
- `process_entry()` converts one schema record into an `ldb_message`.
- `process_file()` streams input, skips comments/blank lines, accumulates complete records, calls `process_entry()`, writes LDIF via `ldb_ldif_write_file()`, and returns conversion counts/failures.

## Control Flow

`process_file()` reads one character at a time. It ignores `#` comments and blank lines, grows a talloc buffer as needed, and calls `check_braces()` whenever a newline is seen inside a record. Once a full record is found, `process_entry()` determines whether the entry is an attribute or object class, extracts the OID, creates a deterministic `schemaIdGuid` from SHA-256 of that OID, then walks schema tokens until `)`. Token handlers populate LDB attributes; syntax tokens are translated through `find_syntax_map_by_standard_oid()`. Successful messages are written as LDIF; failed records increment `failures`.

## State and Persistence Behavior

The converter stores no durable state except the output LDIF stream. All parse and LDB message memory is talloc-scoped. `process_entry()` steals successful messages to the caller context and frees failed temporary contexts. `process_file()` updates only the returned `struct schema_conv` counters.

## Dependencies and Integration Points

It depends on LDB message/LDIF APIs, DSDB schema syntax maps, GUID helpers, and GnuTLS SHA-256 hashing. It is used by `main.c` for the command-line tool and by `test.c` for cmocka parser regression tests.

## Risks and Edge Cases

The parser is intentionally narrow. It only supports the first `NAME` alias, treats unknown tokens as fatal, and has TODOs for equality/ordering/substr behavior. Unknown syntax OIDs lead to missing syntax fields and can make entries invalid. `check_braces()` enforces a space before a final closing brace. Parsing is hand-written and sensitive to quoting, multiline records, and malformed parentheses. The generated schema GUID is deterministic but not an AD-originated GUID.

## Test Signals

Useful signals are correct record/failure counts, emitted LDIF for valid attribute/objectclass inputs, deterministic `schemaIdGuid`, proper multi-value splitting for `$` lists, and failure on malformed tokens, unterminated values, missing names, or unsupported syntax mappings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/utils/oLschema2ldif/lib.c -->
