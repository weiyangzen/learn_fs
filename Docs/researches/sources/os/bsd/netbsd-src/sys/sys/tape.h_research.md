# File Research: sources/os/bsd/netbsd-src/sys/sys/tape.h

Read completely: 82 lines.

Defines tape device statistics structures exposed to kernel and userland.

Key elements:
- `TAPENAMELEN` fixes tape device name storage for sysctl export.
- `struct tape_sysctl` is the 64-bit-alignment-safe exported statistics format.
- `struct tape` tracks name, busy state, read/write transfer counts, bytes, attach time, last timestamp, total busy time, and list linkage.
- Defines `TAILQ_HEAD(tapelist_head, tape)` so userland can inspect the tape stats list shape.

Risks and notes:
- `struct tape_sysctl` is an exported statistics ABI; field order and widths matter.
- Time fields are split into 32-bit seconds/useconds for stable export layout.
