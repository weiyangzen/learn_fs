# File Research: sources/os/plan9/plan9/sys/src/cmd/wikifs/testwrite.c

This is a test utility for writing a parsed wiki history file into the wiki store.

Behavior:
- Opens a supplied wiki/history file.
- Parses it with `Brdwhist`.
- Converts the last document back to serialized text with a fresh `D<time>` header and `pagetext(..., dosharp=1)`.
- Calls `writepage(atoi(argv[1]), t, h, doc->title)`.

Options:
- Code accepts `-t` to specify expected version timestamp, though usage text says `[-d dir]` and does not match implementation.

Role:
- Developer/test helper for exercising `writepage` conflict and storage behavior.
