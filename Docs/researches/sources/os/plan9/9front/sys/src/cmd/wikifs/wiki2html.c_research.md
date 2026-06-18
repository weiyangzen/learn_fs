# File Research: sources/os/plan9/9front/sys/src/cmd/wikifs/wiki2html.c

Command-line wiki renderer/debugger for HTML output.

Key behavior:
- Options choose wiki directory, history view, old-page view, diff view, or parsed-node dump.
- Uses `gethistory()` for history/diff and `getcurrent()` otherwise, interpreting the argument as a numeric wiki id.
- `-P` prints parsed nodes with `printpage()`; otherwise writes `tohtml()` output to stdout.
- Uses private namespace rforking.

Notable dependencies:
- Wiki cache/storage and rendering APIs.

Research notes:
- `parse` is not initialized unless `-P` is supplied, so the later `if(parse)` reads an uninitialized local in the no-`-P` path.
