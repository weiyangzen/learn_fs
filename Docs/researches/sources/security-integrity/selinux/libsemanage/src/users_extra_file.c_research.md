# sources/security-integrity/selinux/libsemanage/src/users_extra_file.c

## Purpose
File-backed parser/printer for user extra prefix records.

## APIs and persistence
`user_extra_print()` writes `user NAME prefix PREFIX;`. `user_extra_parse()` validates that grammar and stores parsed name/prefix. Init/release bind the extra record table to `SEMANAGE_FILE_DTABLE`.

## Dependencies and risks
Uses `parse_utils` and `database_file`. Prefix values cannot include semicolons without parser support. Like other file adapters, malformed lines are disposed and returned as parse errors.
