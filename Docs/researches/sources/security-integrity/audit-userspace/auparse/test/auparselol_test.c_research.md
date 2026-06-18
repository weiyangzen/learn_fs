<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/auparselol_test.c -->
# sources/security-integrity/audit-userspace/auparse/test/auparselol_test.c

Purpose: command-line feed-mode exerciser for auparse, based on manual-page sample code. It can summarize parsed events or reconstruct raw records for comparison with sed-normalized audit logs.

Important APIs and functions: `print_escape` emits strings while escaping selected characters; `auparse_callback` handles `AUPARSE_CB_EVENT_READY`, iterates records and fields, and either prints summaries/verbose interpretations or reconstructs raw audit records in `--check` mode; `main` parses `--stdin`, `-f/--file`, `--verbose`, `--check`, and `--escape`, sets global escape mode, feeds input chunks, flushes, and destroys the parser.

Control flow and state: global `flags` controls behavior. `event_cnt` is heap allocated and registered as callback user data with `free` cleanup through `auparse_add_callback`. Input is read in 2048-byte chunks and streamed to an `AUSOURCE_FEED` parser.

Dependencies and integration: depends on `libaudit.h`, `auparse.h`, stdio/getopt, and fixture logs. The shell wrappers compare `--check` output against `auditd_raw.sed` normalized raw logs.

Risks and test signals: the check mode intentionally ignores synthetic `type` and `node` fields while reconstructing headers from timestamp/type APIs, making it sensitive to parser record assembly. Potential risks include global escape state, limited diagnostics, and typo-prone raw formatting. A clean sorted diff is the primary pass signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/auparselol_test.c -->
