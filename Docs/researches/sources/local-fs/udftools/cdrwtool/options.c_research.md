# File Research: sources/local-fs/udftools/cdrwtool/options.c

Command-line parser for `cdrwtool`.

Defines long and short options for:
- Help.
- Device selection.
- Get/set write parameters.
- Blank mode: `full` or `fast`.
- Format block count.
- Run mkudffs on a track.
- UDF revision selection.
- Write speed.
- Fixed/variable packet mode.
- Quick setup with optional block count.
- Reserve track.
- Close track/session.
- Packet size.
- Border/session setting.
- Write type: `mode1` or `mode2`.
- Input file and write offset.
- Detailed disc info.

`usage` prints package name/version and iterates the long option table.

`parse_args` mutates `struct cdrw_disc` and device path directly. Most numeric values are parsed with `strtol`/`strtoul`. UDF revision is bounded to `0x0150` through `0x0201` and checked with `udf_set_version`.

Notable quirks:
- Long option names include spaces, matching historical usage text more than conventional GNU long-option style.
- Most numeric options have no range or trailing-character validation.
- The short option string includes `C` for close session even though the long option table only maps `"close track"` to `c`.
