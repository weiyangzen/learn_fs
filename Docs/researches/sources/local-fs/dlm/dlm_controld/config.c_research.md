# File Research: sources/local-fs/dlm/dlm_controld/config.c

## Purpose
Parses `dlm.conf` for daemon options and per-lockspace master/weight configuration, and supports runtime option changes from distributed helper-run commands.

## Main Behavior
- `get_weight()` returns DLM master weight for a node in a lockspace: default weight is 1 when no masters are configured; non-listed nodes get weight 0 when a master list exists.
- `setup_lockspace_config()` scans `/etc/dlm/dlm.conf` for `lockspace <name>` sections, applies `nodir=`, and reads following `master <name> node=<id> [weight=<n>]` lines.
- Generic option parsing supports int, uint, bool, and string daemon options from `key=value` lines. CLI settings take precedence over config-file values, which take precedence over defaults.
- `set_opt_file(update)` reads the config file:
  - Initial mode populates file values.
  - Update mode only applies options marked reloadable and detects reloadable file options that were removed/commented out.
  - Reload actions currently include writing `log_debug` to configfs and updating logfile priority.
- Dynamic online configuration is parsed by `set_opt_online()`, using the same argument tokenizer as the helper command parser. It supports `restore_all` and per-option `restore`.

## Integration Points
- Uses `dlm_options[]` defined elsewhere and `get_ind_name()` from `main.c`.
- Calls `set_configfs_opt()` from `action.c` and `set_logfile_priority()` from `logging.c` for live reload effects.
- Per-lockspace master weights feed `set_configfs_members()` in `action.c`.

## Risks and Notes
- Parser is intentionally simple and whitespace-sensitive; it is not a general config grammar.
- String parsing uses fixed `MAX_LINE` buffers and `strcpy`/`strdup`; valid config lines are expected to fit 256 bytes.
- Dynamic string option changes allocate a new `dynamic_str` without freeing any previous dynamic string before assignment in that path; reset frees it later.
- `set_opt_online()` returns early on malformed escaping and does not free duplicated argument strings, acceptable for infrequent control operations but still a leak.
