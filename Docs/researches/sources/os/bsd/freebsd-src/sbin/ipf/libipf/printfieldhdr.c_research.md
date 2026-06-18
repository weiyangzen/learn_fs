# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printfieldhdr.c

Field-header printer for tabular output.

Key behavior:
- Supports `"all"` sentinel value `-2` by recursively printing all positive fields.
- Prints caller-supplied header overrides as-is.
- Uppercases default field names for display.

Research notes:
- Duplicates the field name with `strdup()` only when using the default table word.
