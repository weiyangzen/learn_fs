# sources/security-integrity/selinux/libsemanage/src/seusers_file.c

## Purpose
Adds file-backed parsing and printing for seuser mappings.

## APIs and persistence
`seuser_print()` emits `name:sename[:mls]`. `seuser_parse()` consumes colon-separated fields with optional MLS range, skipping blank/end lines and disposing malformed lines. `seuser_file_dbase_init()` binds the generic seuser record table to `SEMANAGE_FILE_DTABLE`.

## Dependencies and integration
Uses `database_file`, `parse_utils`, and `seuser_internal` accessors. The backend persists local login mappings in files such as `seusers.local`.

## Risks and test signals
The MLS parser is noted as not allowing spaces/multiline. Error recovery disposes the current parse line. Formatting has no escaping, so field delimiters in names or ranges are not representable.
