# File Research: sources/os/plan9/plan9/sys/src/cmd/wikifs/wiki2html.c

This is a command-line renderer for wiki pages to HTML.

Options:
- `-d dir`: sets `wikidir`.
- `-h`: render history view.
- `-o`: render old page view.
- `-D`: render diff view.
- `-P`: print parsed page node dump instead of HTML.

Behavior:
- Uses page number argument.
- Loads full history for history/diff, otherwise current page.
- Optionally dumps parser output with `printpage`.
- Calls `tohtml` on the latest document and writes to stdout.

Notable issue:
- Local `parse` is not initialized before option parsing; if `-P` is not supplied, its value is indeterminate in standard C.
