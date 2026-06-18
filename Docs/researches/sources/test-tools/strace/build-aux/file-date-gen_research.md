<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/build-aux/file-date-gen -->
# sources/test-tools/strace/build-aux/file-date-gen

Purpose: shell helper that emits a formatted UTC date for a source file, supporting reproducible release metadata.

Important logic: optional `-f DATE_FORMAT`; inputs are `FILE`, optional date-file path defaulting to `.<basename>.date`, and optional default date. Fallback order is date file, latest Git log commit date for the file, default date, `SOURCE_DATE_EPOCH`, and current UTC date. It formats with GNU `date -u "+$DATE_FORMAT" -d "$date"`.

Control flow: validates required file argument and formatted date result, then `exec printf`.

State and persistence: reads metadata and writes stdout only.

Dependencies and integration: used for manpage or release dates in `Makefile.am` distribution hooks.

Risks: GNU date dependency and Git availability. If a file was renamed or absent from Git history, fallback behavior determines output. Test signals: run against a tracked file, a file with adjacent `.file.date`, and a tarball with `SOURCE_DATE_EPOCH`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/build-aux/file-date-gen -->
