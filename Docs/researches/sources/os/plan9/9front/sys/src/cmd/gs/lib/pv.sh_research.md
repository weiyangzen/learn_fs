# File Research: sources/os/plan9/9front/sys/src/cmd/gs/lib/pv.sh

Shell helper for previewing a specified page of a DVI file in Ghostscript.

Behavior:
- Requires at least `page_number file_name[.dvi]`.
- Uses `dvips -p $PAGE -n 1 $FILE ... -o $FILE.$$.pv` to render one page to temporary PostScript.
- Runs Ghostscript on the temporary file.
- Installs a trap to remove `$TEMPDIR/$FILE.$$.pv`; `TEMPDIR` defaults to `.`.

Notes:
- Older fixed-resolution handling is commented out; script relies on modern `dvips` configuration.
- The trap path and output path differ slightly if `FILE` includes path components because `dvips` writes `$FILE.$$.pv` relative to invocation.

Filesystem relevance:
- Temporary-file conversion/preview wrapper; no filesystem internals.
