# File Research: sources/os/plan9/plan9/sys/src/cmd/wikifs/wiki2text.c

This command-line utility converts a wiki history file to serialized wiki text.

Options:
- `-d dir`: sets `wikidir`, though this utility opens the supplied file directly with `Bopen`.

Behavior:
- Parses the input history file with `Brdwhist`.
- Iterates over every document version.
- Prints a separator for each index.
- Converts each parsed page back to text with `pagetext(..., dosharp=1)` and writes to stdout.

Role:
- Debug/conversion helper for inspecting parser and serializer behavior across all history versions.
