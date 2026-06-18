<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/request-key.c -->
# sources/security-integrity/keyutils/request-key.c

## Purpose

`request-key.c` is the `/sbin/request-key` helper that the kernel invokes to resolve, instantiate, negate, or reject keys. It parses kernel-provided request parameters, discovers the requested key type/description/callout info, selects the best matching action from request-key configuration files, expands macros, and executes or pipes data through the chosen program.

## Important APIs, Types, and Functions

`struct parameters` stores key ID, operation, requestor IDs/keyrings, key type/description, callout info, and cached string lengths. Main helpers are `lookup_action()`, `scan_conf_dir()`, `scan_conf_file()`, wildcard `match()`, `execute_program()`, and `pipe_to_program()`. Diagnostic helpers are `debug()`, `error()`, and signal handler `oops()`. It uses `keyctl_assume_authority()`, `keyctl_describe_alloc()`, `keyctl_read_alloc()`, and `keyctl_instantiate()`.

## Control Flow

`main()` handles `--version` and debug/local/no-log/verbose options, validates seven or eight kernel arguments, ensures stdio fds are open, optionally assumes authority over the requested key, describes the key, retrieves callout info if omitted, and calls `lookup_action()`. Lookup scans `/etc/request-key.d/*.conf` before `/etc/request-key.conf` unless local-dir mode is selected. Each config line matches operation, type, description, and callout info with one `*` wildcard per field; the least-wild match wins. `execute_program()` tokenizes the command, expands `%` macros and `%{type:desc}` keysub reads, then either `execv()`s or invokes `pipe_to_program()` for `|` commands. Pipe mode concurrently writes callout info to child stdin, collects payload from stdout, logs stderr, and instantiates the key; child failure recursively switches to `negate`.

## State and Persistence Behavior

Global state tracks verbosity, local-dir/no-log/debug flags, current config file/line, recursion guard, selected command, and wildcard score. Kernel state changes include assuming request authority, reading the authorization key, instantiating successful payloads, or delegating negate/reject actions. Filesystem reads are config files/directories and executed helper programs; syslog receives debug/errors unless disabled.

## Dependencies and Integration Points

The helper integrates with kernel request-key upcalls, `/etc/request-key.d`, `/etc/request-key.conf`, `request-key-debug.sh`, key resolver programs such as `key.dns_resolver`, syslog, and libkeyutils. It relies on trusted configuration because commands execute with helper privileges and receive kernel/requestor context.

## Risks and Edge Cases

Config parsing is whitespace-token based with no shell quoting. Command and line buffers are fixed at about 4096 bytes; pipe payload is capped at 32768 bytes. Macro expansion passes arguments directly to `execv()` but keysub macro data must be printable. Wildcard scoring prefers less wildcard consumption but ties keep the first selected command. Recursive negation is guarded by `norecurse` but misconfigured negate actions can still fail the request. Local-dir debug mode changes config search roots.

## Test Signals

Requesting tests exercise invalid type/description/callout bounds, direct callouts, piped callouts, attachment to destination/session keyrings, negative results, and config-driven debug helper behavior. Additional validation should include directory precedence, wildcard specificity, keysub macros, stderr logging, and child failure recursion.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/request-key.c -->
