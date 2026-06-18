# sources/security-integrity/selinux/libsemanage/src/database_file.h

Purpose: declares the generic file-backed database interface.

Important APIs/types/functions: `record_file_table_t` supplies a `parse` callback from `parse_info_t` into a record and a `print` callback from record to `FILE *`; `dbase_file_init`, `dbase_file_release`, and `SEMANAGE_FILE_DTABLE` expose the backend.

Control flow: object-specific code combines its generic `record_table_t` with a file parse/print table, then generic CRUD operates against the linked-list cache and flushes through the printer.

State and persistence behavior: file backends persist complete record sets to writable text files and cache parsed read-only contents in memory.

Dependencies and integration points: includes stdio, `parse_utils.h`, `database.h`, and internal `handle.h`. Used for local customizations such as booleans and other semanage text databases.

Risks: parse callbacks must return `STATUS_NODATA` on EOF and handle NULL streams. Test signals are parser/printer round trips and robust handling of empty or absent files.
