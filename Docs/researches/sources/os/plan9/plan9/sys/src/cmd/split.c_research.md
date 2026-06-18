# File Research: sources/os/plan9/plan9/sys/src/cmd/split.c

Plan 9 `split` command implementation.

Key responsibilities:
- Splits input by fixed line count (`-n`/`-l`) or regex boundaries (`-e`).
- Writes sequential output files named by stem plus suffix, default `xaa`, `xab`, etc.
- Supports regex-captured output names, suffix appending, case-insensitive matching, and suppressing matched lines with `-x`.

Important functions:
- `main`: parses options, opens optional input file, drives line or pattern splitting.
- `nextfile`: advances two-letter suffix through `aa`..`zz`.
- `matchfile`: opens file named by regex submatch or next suffix.
- `openf`: creates and initializes output `Biobuf`.
- `fold`: lowercases ASCII for case-insensitive regex matching.

Risks/quirks:
- Only supports two-letter suffix range; after `zz`, reports unsplit remainder once.
- `name[200]` can be overflow-prone when regex capture plus suffix exceeds expectations.
- Error string in `openf` says `grep: can't create`, likely copy/paste.
