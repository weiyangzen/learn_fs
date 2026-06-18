# sources/security-integrity/selinux/libsemanage/src/booleans_file.c

Purpose: implements boolean record parsing and printing for the local file-backed boolean database.

Important APIs/types/functions: `bool_print` writes `name=value`; `bool_parse` parses names, `=`, and values accepting true/false case variants or integer 0/1; `SEMANAGE_BOOL_FILE_RTABLE` supplies the file extension table; init/release wrap `dbase_file_init` and `dbase_file_release`.

Control flow: the generic file database reads lines into parse info, creates a boolean record via `SEMANAGE_BOOL_RTABLE`, and calls `bool_parse`. Parsed names go through `semanage_bool_set_name`, values are validated, and trailing space/end-of-line is asserted. Printing is the reverse for flush.

State and persistence behavior: local boolean defaults persist in text files under the semanage store. The backend caches records in memory, marks modifications, and rewrites the writable file on flush/commit.

Dependencies and integration points: depends on parse utilities, debug macros, file database backend, and boolean record substitution logic.

Risks: malformed values, invalid lines, or name-substitution failures abort parsing. Rewriting all records means printer correctness affects persistence. Test signals include parse round trips for true/false/0/1, malformed-value diagnostics, EOF handling, and commit file contents.
