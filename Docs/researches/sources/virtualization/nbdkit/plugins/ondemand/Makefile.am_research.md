# File Research: sources/virtualization/nbdkit/plugins/ondemand/Makefile.am

## Purpose
Builds the `ondemand` plugin and generates its embedded default shell command.

## Main Contents
Generates `default-command.c` from `default-command.sh.in` by stripping comments, escaping quotes, replacing `__TRUNCATE__`, and forming a C string. Builds `nbdkit-ondemand-plugin.la` from generated command source, `ondemand.c`, and the plugin header. Links common utils and replacement compatibility libraries. Documentation generation produces `nbdkit-ondemand-plugin.1`.

## Dependencies
Disabled on Windows because it needs `open_memstream` and other non-ported behavior. Uses `SED`, `TRUNCATE`, common nbdkit build rules, and optional POD support.

## Risks and Notes
Generated C source embeds shell code at build time, so changes in `TRUNCATE` or the script template affect runtime default behavior. The source is a built artifact and must stay synchronized with the template.
