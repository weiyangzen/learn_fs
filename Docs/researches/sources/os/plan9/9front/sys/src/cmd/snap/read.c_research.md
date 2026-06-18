# File Research: sources/os/plan9/9front/sys/src/cmd/snap/read.c

Purpose: Reads serialized process snapshot files into in-memory `Proc`, `Seg`, `Page`, and `Data` structures.

Key routines:
- `findpid`: locates a process in the loaded list.
- `findpage`: resolves a page reference by pid, memory/text type, and aligned offset.
- `Breadnumber`, `Breadulong`, `Breaduvlong`: parse fixed-width decimal fields with space padding.
- `readdata`: reads a length-prefixed proc metadata section.
- `readseg`: reads segment offset/length and page records. Page records can be zero (`z`), raw (`r`), or references to earlier memory/text pages (`m`/`t`).
- `readsnap`: validates header, iterates process sections, reads known proc files, memory segments, and text segments.

Integration: Used by `snapfs.c` to replay a snapshot as a 9P `/proc`-like tree.

Risks:
- The file format is custom, positional, and fatal on malformed references.
- Page references can only point to already loaded process/page data.
- Alignment to `Pagesize` is enforced for referenced pages.
