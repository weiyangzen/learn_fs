# File Research: sources/os/plan9/9front/sys/src/cmd/venti/root.c

Purpose: Prints decoded Venti root blocks.

Key behavior:
- Connects to a Venti server and processes one or more root scores.
- Reads each score as `VtRootType`, validates root block size, unpacks `VtRoot`, and prints score, quoted name/type, root data score, block size, and previous root score.
- Continues after parse/read/unpack failures for individual arguments.

Dependencies:
- Uses Venti root unpacking, score parsing, connection APIs, and quote formatting.

Notable details:
- Hard-checks the read size against `VtRootSize`.
