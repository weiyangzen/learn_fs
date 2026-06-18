# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/common/request.c

`request.c` handles special PostScript request insertion. It stores `-R` style requests, associates them with global setup or a page number, and dumps matching request bodies from a request file when requested.

Request files use `@keyword` markers; matching bodies are copied until the next marker, ignoring comment lines beginning with `#` or `%`.
