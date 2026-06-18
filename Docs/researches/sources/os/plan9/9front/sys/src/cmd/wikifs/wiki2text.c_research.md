# File Research: sources/os/plan9/9front/sys/src/cmd/wikifs/wiki2text.c

Command-line converter from a wiki history file to raw wiki text for each revision.

Key behavior:
- Optional `-d` sets `wikidir`, though input is read directly from the provided file path.
- Reads a history file with `Brdwhist()`.
- Iterates all revisions, printing a separator and `pagetext(..., dosharp=1)` output for each.

Notable dependencies:
- Wiki history parser and text renderer.

Research notes:
- Error message on `pagetext()` failure says `wiki2html`, reflecting copy/paste from the HTML tool.
