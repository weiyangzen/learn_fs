# sources/test-tools/kdevops/scripts/config

Purpose: command-line helper for editing Kconfig-style `.config` files.

Important APIs/types/functions: environment prefix `CONFIG_`, delimiter `SED_DELIM`, `usage`, `checkarg`, `txt_append`, `txt_subst`, `txt_delete`, `set_var`, `undef_var`, command parsing for enable/disable/module/set-str/set-val/undefine/state/*-after/refresh, and `make oldconfig`.

Control flow: parses optional `--file`, collects commands, uppercases symbols unless `--keep-case`, normalizes symbols by removing prefix, executes repeated mutations against the config file, supports inserting after an anchor, prints option state, and refreshes through `make oldconfig`.

State/persistence behavior: mutates `.config` or the file named by `--file` using temporary `.swp` files and `mv`; `--refresh` can also update config through Kconfig.

Dependencies/integration: derived from Linux kernel config tooling patterns and used by kdevops Make/Kconfig automation.

Risks/test signals: sed-based regex matching can mis-handle special characters; append-after uses both enabled and disabled anchors; no file locking. Test signals are correct config lines after each command, correct `--state` output, and successful `--refresh`.
