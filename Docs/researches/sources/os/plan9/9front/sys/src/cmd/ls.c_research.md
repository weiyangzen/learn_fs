# File Research: sources/os/plan9/9front/sys/src/cmd/ls.c

This is Plan 9 `ls`. It stats files or reads directories, accumulates `Dir` entries, sorts them unless `-n`, computes column widths, and formats output.

Supported flags include long format, directory-as-file, muid, no sort, full path prefixing, qid/version/type, reverse, block size, time sort, temporary flag display, access-time selection, executable/directory suffixes, and unquoted output.

Important functions:
- `ls()` handles stat/open/dirreadall and prefix cleanup.
- `output()` sorts and flushes pending entries.
- `dowidths()` computes field widths for aligned output.
- `format()` prints one entry with selected metadata.
- `compar()` sorts by name/prefix or time, with reverse support.
- `asciitime()` chooses time/year display based on age.
- `xcleanname()` collapses duplicate and trailing slashes.

It is a direct Plan 9 filesystem metadata formatter using `Dir` and qid fields.
