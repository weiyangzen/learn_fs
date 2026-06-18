# sources/user-network-fs/samba/source4/torture/shell.c

## Purpose
`shell.c` implements smbtorture's interactive command shell. It provides a readline-driven REPL that lets users inspect and change torture settings, credentials, and targets, list registered suites, and run named tests without restarting the process.

## Important APIs, Types, And Functions
`struct shell_command` maps a command name to a handler, usage string, and help text. The `commands[]` table defines `auth`, `help`, `list`, `quit`, `run`, `set`, and `target`. `torture_shell()` owns the REPL loop using `smb_readline()`, optional `add_history()`, and `poptParseArgvString()`. `shell_set()` dumps or updates loadparm settings via `lpcfg_dump()` and `lpcfg_set_cmdline()`. `shell_run()` calls `torture_run_named_tests()`. `shell_list()` calls `torture_print_testsuites()`. `shell_auth()` reads and mutates global command-line credentials through `cli_credentials_get_*()` and `cli_credentials_set_*()`. `shell_target()` prints or parses target strings with `torture_parse_target()`. `match_command()` supports full command names and one-character abbreviations.

## Control Flow
Before entering the loop, `torture_shell()` sets an empty guessed password if none was specified to avoid credential prompts during `auth` display. Each prompt reads one line, parses it into argc/argv, scans the command table for a full-name or single-letter match, shifts off the command token, and invokes the matching handler. Handlers either print usage on invalid arity, mutate the shared torture context, or call into the existing smbtorture registry. `quit` exits the whole process with `exit(0)`. Unknown commands are ignored after parsing because no fallback message is emitted.

## State And Persistence
The shell keeps no persistent private state beyond readline history. It mutates process-global command-line credentials and the in-memory loadparm/torture context, so later commands and tests in the same shell session observe changed authentication, target, and configuration values. No changes are written back to smb.conf or other files by this code.

## Dependencies
Dependencies include Samba's readline wrapper, popt argument parsing, command-line credentials, loadparm, smbtorture registry functions, and target parsing helpers. Behavior depends on the global credential object returned by `samba_cmdline_get_creds()` and the active `torture_context`.

## Integration Points
This file is an operator-facing control surface over the broader smbtorture runtime. It integrates test discovery and execution with configuration mutation and credential management. It does not register tests itself; it calls into already-registered suites and shared command-line state.

## Risks
The REPL does not handle empty parsed input before reading `argv[0]`, so a blank or whitespace-only line may dereference invalid data depending on `poptParseArgvString()` output. Parsed `argv` is not freed in the loop, which can leak memory in long sessions. One-letter abbreviations can become ambiguous if future commands share initial letters; the first table match wins. The `auth` command prints the current password to stdout. Unknown commands produce no diagnostic, which can confuse interactive users.

## Test Signals
Signals are successful parsing and dispatch for full and abbreviated commands, correct usage output for wrong arity, successful mutation of credentials and target settings, visible suite listing, and `run TESTNAME` invoking registered tests. Robustness tests should include blank lines, malformed quoting, unknown commands, long sessions, and credential display after no password was supplied.
