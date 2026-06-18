# File Research: sources/virtualization/nbdkit/server/options.h

Purpose: Defines CLI option constants, getopt tables, and helper logic for distinguishing short plugin/filter names.

Option definitions:
- Enum values beyond `CHAR_MAX` represent long-only options such as `--dump-config`, `--dump-plugin`, `--filter`, `--log`, `--tls-*`, `--vsock`, and others.
- `short_options` is `46D:e:fg:i:nop:P:rst:u:U:vV`.
- `long_options` maps aliases such as `--read-only`/`--readonly`, `--unix`, `--stdin`, `--new-style`, `--old-style`, `--print-uri`, and TLS options to getopt codes.

Helper:
- `is_short_name(filename)` returns true only for simple plugin/filter names without path separators, spaces, dots, commas, equals, path-list separators, or control characters.
- It also rejects strings containing `DIR_SEPARATOR_STR`.

Role in server:
- Included by `main.c` to drive `getopt_long` parsing and resolve plugin/filter short names to install directories.
