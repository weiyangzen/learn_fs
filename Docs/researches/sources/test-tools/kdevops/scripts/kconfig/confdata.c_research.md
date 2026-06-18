# sources/test-tools/kdevops/scripts/kconfig/confdata.c

## Purpose
`confdata.c` owns Kconfig configuration persistence. It reads `.config`-style files into symbol defaults, tracks whether configuration changed, writes normal and minimal configs, optionally writes YAML, and generates build-time autoconf files and dependency stamp files.

## Important APIs, Types, And Functions
Public functions include `conf_get_configname()`, `conf_read_simple()`, `conf_read()`, `conf_write_defconfig()`, `conf_write()`, `conf_write_autoconf()`, `conf_set_changed()`, `conf_get_changed()`, `conf_set_changed_callback()`, `conf_set_message_callback()`, and `conf_errors()`. Important internal helpers include `is_same()`, `make_parent_dir()`, `conf_set_sym_val()`, `getline_stripped()`, `escape_string_value()`, `__print_symbol()`, YAML helpers, `print_symbol_for_c()`, `print_symbol_for_rustccfg()`, `conf_touch_deps()`, and `__conf_write_autoconf()`.

## Control Flow
Reading starts with `conf_read_simple()`, which opens an explicit config or falls back to `KCONFIG_CONFIG` and `KCONFIG_DEFCONFIG_LIST`, clears prior defaults for the selected definition slot, then parses `CONFIG_FOO=value` and `# CONFIG_FOO is not set` lines. Unknown symbols either warn or touch dependency files when reading `auto.conf`. `conf_read()` calculates all symbols and marks changed when saved and calculated values differ. Writing `.config` creates a temp file unless `KCONFIG_OVERWRITECONFIG` is set, walks the menu tree in display order, writes headings and symbol values, compares with the existing file, renames `.old`, and clears changed state. Autoconf generation writes a `.cmd` depfile, touches changed include/config dependency files, calculates symbols, writes C header, Rust cfg, then writes `auto.conf` last.

## State And Persistence
Persistent paths are controlled by `KCONFIG_CONFIG`, `KCONFIG_AUTOCONFIG`, `KCONFIG_AUTOHEADER`, `KCONFIG_RUSTCCFG`, and `KCONFIG_YAMLCFG`. YAML all-symbol behavior comes from `KCONFIG_YAMLCFG_ALL`. The file uses global `autoconf_cmd`, warning counters, `conf_changed`, callbacks, and dependency path buffers. It mutates `sym->def[]`, `sym->flags`, and choice member ordering.

## Dependencies And Integration Points
It depends on POSIX file APIs, `mmap`, Kconfig symbols/menus, `xalloc`, `zconf_fopen()`, and string builders from `lkc.h`. `conf.c` and frontends call it to load, save, and sync generated configuration state.

## Risks And Test Signals
`is_same()` maps zero-length files without a special case, which can be platform-sensitive. YAML string output performs simple quoting and does not escape embedded quotes. `conf_name_to_yaml()` currently lowercases names but leaves underscores, despite a redundant branch. Atomicity relies on rename in the same filesystem. Tests should cover malformed configs, unknown symbols with warning envs, string escaping, YAML output, no-change detection, overwrite mode, autoconf ordering, and dependency touch behavior.
