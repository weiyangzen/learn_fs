<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/toolbox.inc.sh -->
# sources/security-integrity/keyutils/tests/toolbox.inc.sh

## Purpose
Large shared shell toolbox for keyutils tests. It wraps `keyctl` subcommands, logs commands/output, captures IDs and payloads, checks errno text, validates notifications, and maintains the shared `result` state.

## Important APIs, Types, And Functions
Core helpers include `marker`, `failed`, `expect_args_error`, `toolbox_report_result`, `toolbox_skip_test`, `expect_error`, `create_key`, `create_keyring`, `list_keyring`, `describe_key`, `print_key`, `revoke_key`, `unlink_key`, `update_key`, `search_for_key`, `set_key_perm`, `new_session`, `timeout_key`, `invalidate_key`, `supports`, `watch_key`, and `expect_notification`.

## Control Flow
At source time it detects endianness, computes maximum test strings and page-sized payloads, records quota/GC delay defaults, and defines wrappers. Each wrapper logs the command, executes it with expected exit status, extracts final output lines when needed, stores shell variables via `eval`, calls notification checks on successful mutating operations, and invokes `failed` on mismatches.

## State And Persistence Behavior
The toolbox is the main persistence and observation layer for tests: it appends to `$OUTPUTFILE`, may append to `$watch_log` and `$PWD/notify.log`, adds watches for new keys, and mutates kernel keyrings through wrapped `keyctl` operations. `failed` records diagnostics and sets global `result=FAIL`.

## Dependencies And Integration Points
Depends on `keyctl`, `/proc/key-users`, `/proc/keys`, `file`, `getconf`, `grep`, `awk`, `md5sum`, `date`, and version helpers sourced before it. It integrates with notification support prepared by `prepare.inc.sh`.

## Risks And Edge Cases
Many helpers parse the last line of `$OUTPUTFILE`, so extra command output can break expectations. Error matching depends on English errno strings and alternate legacy messages. Several loops wait for lazy kernel key cleanup and can hang if `/proc/keys` behavior changes. `eval` variable assignment requires trusted variable names from tests.

## Test Signals
Signals are command exit status, exact errno classification, key ID extraction, raw keyring lists, raw descriptions, payload strings, unlink counts, and watch notification records.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/toolbox.inc.sh -->
