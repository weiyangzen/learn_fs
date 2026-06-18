# File Research: sources/os/plan9/plan9/sys/src/cmd/snap/snap.h

Shared definitions for the `snap` tools.

Key contents:
- Defines process pseudo-file indexes: `segment`, `fd`, `fpregs`, `kregs`, `noteid`, `ns`, `proc`, `regs`, and `status`.
- Defines internal snapshot page size as 1024 bytes.
- Defines `Data`, `Seg`, `Page`, and `Proc`.
- Declares capture, read, write, page lookup, and allocation helpers.

Important details:
- `Page` records whether it has already been written and where it was first emitted, enabling deduplicated page references.
- `Proc` stores both memory segments and optional text image.

Filesystem relevance:
- Foundational data model for serializing and serving process filesystem snapshots.
