## sources/security-integrity/audit-userspace/src/ausearch-options.c

Purpose: parses `ausearch` CLI options and populates global search, output, checkpoint, and formatting state.

Important APIs/functions: `check_params()` is the public parser. Helpers `audit_lookup_option()`, `usage()`, `convert_str_to_msg()`, and `parse_msg()` map option strings and message type lists. It defines globals consumed throughout the cluster: `user_file`, `force_logs`, `checkpt_filename`, `report_format`, all `event_*` filters, CSV extra flags, `escape_mode`, and `arg_eoe_timeout`.

Control flow: manual argument scanning determines whether the next argv is an argument, switches on a table-driven option id, validates and converts numbers/names, allocates strings/lists, and performs final consistency checks such as requiring CSV for `--extra-*`.

State/persistence: process-global mutable state; no persistence. Allocations are partially freed by `ausearch.c` and related cleanup paths.

Dependencies/integration: uses libaudit message/syscall/machine helpers, passwd/group lookup, `ausearch-time.c`, `ausearch-int.c`, and `auparse-defs` escape modes.

Risks/test signals: the custom parser treats any next argument beginning with `-` as absent except for special negative numeric handlers, so option ordering and negative values need coverage. `--escape` checks `strncmp(optarg, "shell", 6)` before exact `shell_quote`, making `shell_quote` select shell mode rather than shell-quote mode. Globals duplicate `event_type` declaration. Tests should cover every option, invalid/missing args, conflicting formats, negative login/session/exit values, arch before syscall, node list allocation, CSV extra validation, and checkpoint time-only interaction.
