# sources/security-integrity/audit-userspace/audisp/plugins/ids/ids_config.c

Purpose: parses `/etc/audit/ids.conf` into the global IDS tuning structure used by the bad-event and behavior models. It supplies defaults for login thresholds, reaction masks, scoring weights, and timed reaction durations.

Important APIs and data: exports `reset_config`, `free_config`, `dump_config`, and `load_config`. Local parser tables map option names to parser callbacks; `reactions[]` maps names such as `block_address`, `term_session`, and `lock_account_timed` onto bit flags from `ids_config.h`.

Control flow: `load_config` resets defaults, opens the fixed config path, verifies root ownership, non-world-writability, and regular-file status, then reads `name = value` lines through `get_line` and `nv_split`. Unknown keywords, malformed lines with values, or parser failures abort loading; missing config is allowed with defaults.

State and persistence: no heap-owned config state is retained after parsing, so `free_config` is empty. Parsed values live in the caller-owned `struct ids_conf`; timed values are converted to seconds and remain process memory only.

Dependencies and integration: depends on `audit_strsplit`, syslog, `time_string_to_seconds`, and the reaction constants consumed by `reactions.c`. The parser must remain aligned with documented `ids.conf` option names and the event model thresholds.

Risks: line length is capped at 160 bytes and overlong lines are skipped, which can silently leave defaults. `reaction_parser` accepts comma-separated names but does not trim whitespace around tokens. `block_address_time_parser` has custom unit parsing while `lock_account_time_parser` uses the shared time parser, so behavior can diverge.

Test signals: useful tests are malformed permission checks, unknown keywords, reaction-mask combinations, numeric range failures, time suffixes, and missing-file default behavior. No direct tests are present in this subset.
