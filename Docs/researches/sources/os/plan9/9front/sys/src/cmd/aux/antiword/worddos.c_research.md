# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/worddos.c

Word for DOS document initializer.

Key responsibilities:
- Reads the 128-byte Word for DOS header.
- Verifies the Word for DOS magic/version.
- Rejects autosave/fast-saved Word for DOS documents.
- Creates one text block starting at offset 128 with length from the header.
- Invokes property parsing, default tab width parsing, and notes parsing.

Important behavior:
- Text is treated as non-Unicode.
- Property modifier is set to `IGNORE_PROPMOD`.
- Initialization returns Word version `0` only if text block setup succeeds.

Dependencies:
- Version detection, text block list, property dispatcher, tab-stop parser, notes parser.

Research relevance:
- Legacy Word for DOS entry point into the shared conversion pipeline.
