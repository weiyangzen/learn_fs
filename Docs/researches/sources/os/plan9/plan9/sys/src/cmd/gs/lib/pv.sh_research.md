# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/pv.sh

Shell helper for previewing one page of a DVI file in Ghostscript.

Behavior:

- Requires `page_number file_name[.dvi]`.
- Sets `GS_EXECUTABLE=gs`, `TEMPDIR=.`, and installs a trap to remove `$TEMPDIR/$FILE.$$.pv`.
- Runs `dvips -p $PAGE -n 1 $FILE ... -o $FILE.$$.pv`.
- Opens the generated one-page PostScript file with Ghostscript.

The script is an interactive document-preview convenience wrapper.
