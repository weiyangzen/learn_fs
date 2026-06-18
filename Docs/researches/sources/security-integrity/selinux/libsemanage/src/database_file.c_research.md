# sources/security-integrity/selinux/libsemanage/src/database_file.c

Purpose: implements a generic line-oriented file database backend on top of the linked-list cache.

Important APIs/types/functions: `dbase_file_cache`, `dbase_file_flush`, `dbase_file_init`, `dbase_file_release`, and `SEMANAGE_FILE_DTABLE`.

Control flow: cache opens the read-only path if present, creates records via the record table, repeatedly calls the record file parser until `STATUS_NODATA`, and prepends parsed records into the cache. Flush opens the writable path and prints each cached record through the record file table.

State and persistence behavior: caches file records in memory with modification tracking. Flush rewrites the writable database file, so output ordering and complete-list printing define persistence.

Dependencies and integration points: uses `parse_utils`, `database_llist`, debug reporting, stdio, and object-specific parse/print tables such as booleans and other local store record files.

Risks: parser errors abort cache construction; flush failures can leave persistent files stale or partially written depending on file handling. Test signals include missing read-only files, malformed lines, successful rewrite, and cache serial resync.
