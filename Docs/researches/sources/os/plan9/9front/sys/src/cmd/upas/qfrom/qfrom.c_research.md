# File Research: sources/os/plan9/9front/sys/src/cmd/upas/qfrom/qfrom.c

Small filter that quotes Unix mbox `From ` separator lines.

Key responsibilities:
- Reads stdin or named files with `Biobuf`.
- For each line beginning with `From `, writes an extra leading space.
- Writes all content to stdout without changing character encoding.

Filesystem relevance:
- Useful when storing messages in mbox-like files where body lines beginning `From ` must not be interpreted as separators.

Notable constraints:
- Processes files sequentially and writes all output to stdout.
- Does not report per-file errors beyond `sysfatal()`.
