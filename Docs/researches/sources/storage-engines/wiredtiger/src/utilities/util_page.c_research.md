<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_page.c -->
# sources/storage-engines/wiredtiger/src/utilities/util_page.c

Purpose: Implements the `wt page` diagnostic subcommand, which reads/debugs a single page by page id and LSN from a file URI.

Important APIs/functions: `usage` documents required `-p page_id` and `-l lsn`. `util_page` parses options with `__wt_getopt`, converts both numeric arguments through `util_str2num`, canonicalizes the operand with `util_uri(..., "file")`, acquires a data handle via `__wt_session_get_dhandle`, and in diagnostic builds calls `__wt_debug_disagg_page_id(session_impl, page_id, lsn, NULL)`.

Control flow: The command rejects missing `-p`, missing `-l`, and wrong operand counts before opening the handle. It casts public `WT_SESSION` to `WT_SESSION_IMPL` for internal debug APIs, releases the data handle with `WT_TRET`, frees the URI, and converts nonzero internal return codes to utility exit status `1`.

State and persistence behavior: It should be read/debug-only. It temporarily pins a data handle in the session and releases it before returning. No durable metadata or table content is intentionally modified.

Dependencies and integration points: Depends on the utility URI resolver, numeric parser, WiredTiger internal session handle APIs, `HAVE_DIAGNOSTIC`, and the disaggregated page debug function. It is integrated into the `wt` utility command dispatcher and only has useful behavior in diagnostic builds.

Risks: Non-diagnostic builds return `ENOTSUP`, so scripts must not assume availability. Internal debug APIs and direct `WT_SESSION_IMPL` casts make this sensitive to WiredTiger internal ABI changes. Numeric parsing permits `0x`-prefixed values because base 0 is used after the first-digit check, matching the usage text.

Test signals: Expected tests are command-line validation, diagnostic-build page lookup behavior, and non-diagnostic `ENOTSUP` messaging. A mock or diagnostic integration environment is needed for the actual page access path.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_page.c -->
