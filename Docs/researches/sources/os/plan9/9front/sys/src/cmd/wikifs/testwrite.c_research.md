# File Research: sources/os/plan9/9front/sys/src/cmd/wikifs/testwrite.c

Small test utility that reads a wiki history file and writes its latest parsed page into a numbered wiki document.

Key behavior:
- Optional `-t` supplies a base timestamp for conflict checking.
- Reads a history file with `Brdwhist()`, converts the last document to raw wiki text with `pagetext(..., dosharp=1)`, and calls `writepage()`.
- Uses default `wikidir = "."`.

Notable dependencies:
- Wiki parser, formatter, and storage writer APIs.

Research notes:
- Usage text mentions `[-d dir]` but the implemented option is `-t`, not `-d`.
