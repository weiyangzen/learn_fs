<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_misc.c -->
# sources/storage-engines/wiredtiger/src/utilities/util_misc.c

Purpose: Shared utility helpers for the `wt` command-line tool: error reporting, stdin line reading, numeric parsing, flush/drop fallback, usage formatting, allocator wrappers, string duplication, and output-file lifecycle.

Important APIs/functions: `util_cerr` formats cursor-operation errors through `util_err`; `util_err` writes `progname`, optional formatted context, and either `wiredtiger_strerror` or `WT_SESSION::strerror`; `util_read_line` grows a `ULINE` buffer in 1024-byte increments and returns EOF status separately; `util_str2num` parses unsigned decimal/hex strings using WiredTiger's `__wt_strtouq`; `util_flush` checkpoints and drops the URI if checkpoint fails; `util_usage` prints common subcommand help; `util_malloc`, `util_calloc`, `util_realloc`, `util_free`, and `util_strdup` centralize allocation, including optional Windows TCMalloc support; `util_open_output_file` and `util_close_output_file` abstract stdout versus named output.

Control flow: Helpers are mostly leaf functions called by other utility subcommands. Error helpers always return `1` for caller-friendly utility failure. `util_read_line` increments a static line counter, loops over `getchar`, handles expected EOF, unexpected EOF, and missing newline distinctly, and null-terminates the buffer. `util_str2num` rejects a non-digit first byte before calling `__wt_strtouq`, then optionally requires full-string consumption.

State and persistence behavior: Persistent database effect is limited to `util_flush`, which calls `session->checkpoint` and may delete the target with `session->drop` on checkpoint failure. `util_read_line` has process-local state through a static line counter and caller-owned `ULINE` memory. Allocation wrappers must be paired consistently because Windows community TCMalloc uses a different allocation family.

Dependencies and integration points: Includes `util.h`, WiredTiger internal helpers/macros, global `progname` and `usage_prefix`, `WT_SESSION`, `WT_CURSOR`, and optional `<gperftools/tcmalloc.h>` gated by `ENABLE_WINDOWS_TCMALLOC_COMMUNITY_SUPPORT`. Output helpers integrate with commands that optionally write to files.

Risks: `util_flush` drops data on checkpoint failure by design, so callers must only use it where a failed load/create should be discarded. `util_read_line`'s static line counter is not reset between logical streams and is not thread-local. `util_strdup` under non-TCMalloc returns `strdup` memory that must still be released with `util_free`; that is safe only because `util_free` maps to `free` in that build. `util_open_output_file` returns `NULL` on `fopen` failure and callers must check it.

Test signals: Covered indirectly by all utility commands that parse numeric options, read load input, report errors, and write files. Useful focused tests would exercise EOF/no-newline diagnostics, hex and invalid numeric parsing, stdout versus file close behavior, and the checkpoint-failure drop path with a mocked session.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_misc.c -->
