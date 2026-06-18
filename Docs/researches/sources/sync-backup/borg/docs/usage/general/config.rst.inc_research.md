# sources/sync-backup/borg/docs/usage/general/config.rst.inc

Purpose: documents Borg configuration precedence and YAML config-file support.

Important APIs and control flow: precedence runs from source defaults, `$BORG_CONFIG_DIR/default.yaml`, explicit `--config` files in order, full `BORG_CONFIG`, environment variables, then command-line arguments left to right. Config parsing is implemented via `jsonargparse`; `--print_config` prints merged effective YAML and exits.

State and persistence: Borg reads config files and environment; it does not write config except user-directed output redirection from `--print_config`.

Dependencies and integration points: common/subcommand options, jsonargparse naming (`-` to `_`), default config directory discovery, and command-line ordering.

Risks: left-to-right CLI precedence means config files placed late can override earlier arguments. Users may assume `--print_config` ignores arguments after it; docs specify arguments given before it.

Test signals: precedence matrix tests, multiple config file override order, nested subcommand keys, environment overrides, and `--print_config` output validity.
