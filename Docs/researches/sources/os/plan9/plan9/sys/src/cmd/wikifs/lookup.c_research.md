# File Research: sources/os/plan9/plan9/sys/src/cmd/wikifs/lookup.c

This is a tiny diagnostic utility.

Behavior:
- Includes wiki support headers and calls `nametonum(argv[1])`.
- Prints the numeric page id for the given title/name.

Notable omissions:
- No usage checking or `wikidir` initialization is present in this file, so it assumes the surrounding build/run environment supplies a usable default.
