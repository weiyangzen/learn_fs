# File Research: sources/virtualization/nbdkit/plugins/tmpdisk/Makefile.am

Builds the `tmpdisk` plugin on non-Windows platforms.

Key behavior:
- Distributes `default-command.sh.in` and `nbdkit-tmpdisk-plugin.pod`.
- Excludes the plugin on Windows because it requires a shell script.
- Generates `default-command.c` from `default-command.sh.in` by stripping comments, escaping quotes, adding C string line endings, and substituting `__TRUNCATE__` with `$(TRUNCATE)`.
- Builds `nbdkit-tmpdisk-plugin.la` from generated `default-command.c`, `tmpdisk.c`, and the plugin header.
- Includes common utility headers and links `common/utils/libutils.la`.
- Builds manpage/html documentation when POD support is available, inserting the magic-parameter documentation fragment.

Dependencies:
- Shell, sed, truncate tool substitution.
- nbdkit common utils library.
- POD wrapper for documentation.
