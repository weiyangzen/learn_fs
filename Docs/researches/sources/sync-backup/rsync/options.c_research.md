
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/options.c -->
# Research: sources/sync-backup/rsync/options.c

## Purpose
`options.c` is rsync's central command-line and daemon-socket option parser. It defines the global option state consumed throughout the program, maps user-facing options into that state via popt, validates option combinations, parses daemon-only options, and serializes a filtered option set for the remote server side. It also handles rsync-specific compatibility mechanics such as protocol feature flags, argument protection, daemon refuse-options, `--info`/`--debug` verbosity words, and hostspec parsing.

## Important APIs, Types, and Functions
- Global option variables: transfer behavior (`whole_file`, `append_mode`, `inplace`, `delete_*`, `files_from`), metadata preservation (`preserve_*`), daemon/client roles (`am_server`, `am_sender`, `am_daemon`, `am_chrooted`), logging/output (`verbose`, `info_levels`, `debug_levels`, `stdout_format`, `logfile_format`), protocol/compression/checksum choices, and remote command construction state (`remote_options`, `basis_dir`, `alt_dest_type`).
- `struct output_struct`, `info_words`, and `debug_words` define named output categories, default/user/help/limit priorities, and the client/server/sender/receiver locations where each word applies.
- `parse_arguments(int *argc_p, const char ***argv_p)` is the main parser. It mutates global rsync option state and may replace the argv array with leftover positional arguments.
- `server_options(char **args, int *argc_p)` emits the option vector sent to the remote rsync process, using short option packing where safe and long options for features needing explicit values.
- `safe_arg()` shell-quotes or protocol-quotes option and filename arguments depending on `protect_args`, `old_style_args`, sender trust, and wildcard handling.
- `set_refuse_options()`, `parse_one_refuse_match()`, and `create_refuse_error()` implement daemon and build-feature option refusal.
- `parse_size_arg()` parses size suffixes for block size, max/min size, bwlimit, and max allocation. `parse_time()` handles `--stop-at` when `mktime()` is available.
- `check_for_hostspec()` and `parse_hostspec()` parse `host:path`, `host::module`, and `rsync://host[:port]/path` syntaxes, including IPv6 literals.

## Control Flow
Startup initializes global defaults, builds popt option tables, then `parse_arguments()` calls `set_refuse_options()` before creating a popt context. Normal parsing loops over `poptGetNextOpt()` return values and handles special options in a large switch. `--daemon` restarts parsing against the smaller daemon option table, processes `--dparam`, validates daemon-only conditions, and returns early with `am_daemon` set. `--server` similarly restarts parsing without aliases so server and daemon control options cannot be hidden by user aliases.

After popt returns EOF, the parser performs a second validation/normalization pass: environment defaults (`RSYNC_MAX_ALLOC`, `RSYNC_OLD_ARGS`, `RSYNC_PROTECT_ARGS`, `RSYNC_PARTIAL_DIR`, `RSYNC_ICONV`), checksum/compression negotiation, output verbosity expansion, feature checks, conflict checks, delete-mode selection, daemon-filter validation for option paths, backup suffix/dir derivation, log format setup, bwlimit conversion, inplace/append partial-file rules, `--files-from` opening, and trust flags for sender arguments/filters. Errors are stored in `err_buf` and returned as failure; `option_error()` later reports them.

`server_options()` runs after local option parsing. It compacts compatible options into a `-...` argument, appends protocol feature flags via `maybe_add_e_option()`, then conditionally appends long options that the remote side needs. It uses sender/receiver role checks to avoid leaking client-only choices, preserves compatibility aliases such as `--log-format`, and inserts remote options after validating argument count limits.

## State and Persistence
The file is mostly process-global state. Parsing mutates globals that other modules read directly; no durable state is written except indirectly via opened `filesfrom_fd`, initialized logs, and copied argv buffers. `remote_options`, `basis_dir`, `max_alloc_arg`, and many string options retain pointers into popt-copied or allocated memory. The `err_buf` static buffer persists the last parse error. Daemon refusal mutates the in-memory `long_options` table by temporarily abusing `descrip` and rewriting `argInfo`/`val` for refused options.

## Dependencies and Integration Points
The parser depends on rsync core headers, popt, filter parsing, logging, protocol constants, chmod parsing, checksum/compression negotiation, daemon config lookups (`lp_refuse_options`, `lp_charset`), path sanitization/filter checks, and system feature macros. It integrates with `pipe.c` through `remote_options` and `parse_arguments()` in local child startup, with client/server startup through `server_options()`, with daemon config through refuse/filter logic, and with many runtime modules via the exported global flags.

## Risks
This file has high blast radius because option state controls filesystem access, delete behavior, daemon security, protocol compatibility, and argument quoting. Risks include stale refusal coverage when new options are added, subtle conflicts between implied options and daemon-refused options, unsafe quoting if `protect_args`/`old_style_args` cases regress, integer/suffix parsing edge cases, and mutable popt table state leaking between daemon/non-daemon parses. Security-sensitive paths include daemon filter validation, `--files-from` host handling, symlink munging safety, and `am_chrooted` semantics for daemon chroot boundaries.

## Test Signals
Useful signals include rsync option tests for archive/delete/inplace/partial conflicts, daemon `refuse options` acceptance/refusal including wildcards and negations, remote-shell argument quoting tests with spaces/wildcards/leading dashes/tildes, `--files-from` local and remote forms, protocol downgrade tests, `--info`/`--debug` round trips, max/min size parsing, and build-matrix tests with feature macros disabled (`ICONV_OPTION`, ACLs, xattrs, hard links, crtimes, `mktime`, `setvbuf`).
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/options.c -->
