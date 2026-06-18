# File Research: sources/local-fs/dlm/dlm_sand/config.c

This file parses `dlm_sand` configuration from `dlm.conf` and supports runtime option changes through socket commands.

Lockspace/master config:
- `get_weight()` returns lockspace member weight. If no masters are configured, all nodes default to weight 1; if masters exist, non-masters default to 0.
- `setup_lockspace_config()` scans `lockspace <name> ...` lines, applies `nodir=`, and then reads following `master <name> node=<id> [weight=<w>]` lines through `read_master_config()`.
- Master entries populate arrays on the lockspace: node ids and weights.

Option-file config:
- `set_opt_file(update)` parses `DLM_CONF_PATH`, looks up known option names, applies values by type, respects CLI precedence, and optionally reloads only reloadable options.
- It tracks scanned options during update so removed/commented reloadable file options can be reset.
- Parsing helpers handle int, uint, and string `key=value` forms.

Dynamic config:
- `set_opt_online(cmd_str, cmd_len)` tokenizes a command string into at most `MAX_AV_COUNT` arguments with limited escaping.
- `restore_all` clears all dynamic settings.
- `name=restore` clears one dynamic setting.
- Reloadable options can be changed dynamically and `reload_setting()` applies side effects.
- `reset_dynamic()` and `reset_opt_value()` restore effective values according to priority: CLI, file, default.

Reload side effects:
- `log_debug` writes configfs `log_debug`.
- `debug_logfile` changes logfile priority.

Important dependencies:
- Uses option metadata and helpers from `sand_internal.h`: `dlm_options`, `opt()`, `optu()`, `opts()`, option indexes, request argument types.
- Uses `path_exists()` and `set_configfs_opt()` from `action.c`.
- Uses logging from `log.c`.

Notable details:
- File option precedence is conservative: explicit CLI values are never overridden by file reloads.
- Dynamic settings have top priority while set.
- `get_val_str()` uses `strcpy()` into caller-provided fixed buffers; current callers pass `MAX_LINE` buffers.
