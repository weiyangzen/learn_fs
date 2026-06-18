# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/wordmac.c

MacWord 4/5 document initializer.

Key responsibilities:
- Reads the 256-byte MacWord header.
- Verifies MacWord 4/5 magic/version.
- Rejects fast-saved MacWord files.
- Creates one non-Unicode text block from big-endian begin/end text offsets.
- Invokes property parsing and default tab width setup.

Important behavior:
- Uses big-endian header fields for Mac file offsets.
- Does not call notes parsing in this initializer.
- Returns Word version 4 or 5 on success.

Dependencies:
- Version detection, text block list, property dispatcher, tab-stop parser.

Research relevance:
- Legacy Macintosh Word entry point into the shared conversion code.
