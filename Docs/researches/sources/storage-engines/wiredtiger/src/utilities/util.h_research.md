## sources/storage-engines/wiredtiger/src/utilities/util.h

Purpose: central header for the `wt` utility. It imports WiredTiger internals, declares shared global CLI state, exposes all command entry points, and declares helper routines for URI normalization, usage, errors, line reading, numeric parsing, memory allocation, and output-file handling.

Important APIs/types/functions: defines `ULINE` as a managed line buffer used by dump/load readers. Extern globals include `home`, `progname`, `usage_prefix`, `verbose`, `verbose_handler`, and WiredTiger getopt globals. Command prototypes include `util_alter`, `util_backup`, `util_compact`, `util_create`, `util_dump`, `util_list`, `util_load`, `util_loadtext`, `util_verify`, and others. Shared helpers include `util_err`, `util_cerr`, `util_flush`, `util_read_line`, `util_str2num`, `util_uri`, `util_usage`, allocation wrappers, and output-file open/close wrappers.

Control flow: this header does not execute code, but it defines the common command signature `int (WT_SESSION *, int, char *[])` used by `util_main.c` dispatch. Commands share the global getopt state and helper API declared here.

State and persistence behavior: exposes process-wide CLI state such as the active home directory and verbose mode. Helpers declared here affect persistence indirectly: `util_flush` forces loaded data to disk, `util_uri` determines which database object a command mutates, and allocation/output helpers control resource ownership.

Dependencies and integration points: depends on `wt_internal.h`, so utility code is allowed to call internal WiredTiger APIs as well as public `WT_SESSION`/`WT_CONNECTION` APIs. It is included by every utility command source and is the contract between command files and shared `util_misc.c`/`util_verbose.c`.

Risks: because this header exposes internal APIs and process globals, command implementations are tightly coupled and not reentrant. Misuse of `ULINE.mem` ownership or allocation wrappers can leak or double free. Any signature change must be coordinated across all command sources and the dispatcher.

Test signals: full utility target compilation is the main ABI signal. Runtime tests for usage/error output, URI normalization, input line handling, memory-error paths, and output-file close errors exercise the shared helper contract.
