# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/common/misc.c

General helper routines for portable PostScript translators.

Key responsibilities:
- Parses output page ranges into `olist`.
- Tests whether a page number should be output.
- Includes font encoding files.
- Copies files to stdout.
- Parses integers from strings.
- Reports errors and handles interrupt cleanup.

Important behavior:
- `out_list()` accepts troff-style ranges, with missing range end defaulting to 9999.
- `setencoding()` emits an encoding file from `ENCODINGDIR`; if `cat()` fails it toggles `writing` based on whether name starts with `UTF`.
- Fatal errors unlink `temp_file` unless `ignore` is enabled.

Notable risks:
- Several functions use implicit-int K&R style.
- `cat()` ignores short write errors.
