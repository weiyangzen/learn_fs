# File Research: sources/os/plan9/9front/sys/src/cmd/urlencode.c

`urlencode` encodes stdin or a file to application/x-www-form-urlencoded style output, or decodes with `-d`. Encoding preserves alphanumerics and selected punctuation, maps space to `+`, and emits `%XX` uppercase hex for other bytes.

Decoding recognizes valid `%XX` pairs and `+` as space; malformed percent sequences are passed through conservatively. The tool uses buffered Plan 9 I/O and exits after flushing stdout.
