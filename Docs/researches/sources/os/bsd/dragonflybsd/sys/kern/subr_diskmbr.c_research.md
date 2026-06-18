# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_diskmbr.c

MBR and extended-partition parser for DragonFly disk slice discovery, with GPT handoff support.

Key responsibilities:
- Reads the primary MBR, verifies the `0x55aa` signature, and falls back to a compatibility slice if the signature is missing.
- Detects protective GPT in the first DOS partition and delegates to `gptinit()`.
- Detects Ontrack Disk Manager and rereads the MBR from sector 63.
- Rejects historical DragonFly dangerously dedicated partition-table templates.
- Guesses CHS geometry from primary partition entries and updates disk info geometry fields without changing media size/block count.
- Allocates a full `MAX_SLICES` slice structure and populates primary and logical slices.
- Recursively walks extended partitions up to depth 16 and truncates slice count to `MAX_SLICES`.

Important behavior:
- `check_part()` compares CHS-derived sectors with LBA values but permits common pure-LBA and modulo-1024 CHS encodings.
- `mbr_setslice()` clamps/truncates slices extending past media end and special-cases `0xffffffff` size as likely >2TB media.
- Extended partition links use base extended offset for nested links and current extended offset for logical data partitions.

Dependencies:
- Depends on disk slice structures, DOS partition constants/macros, pbuf synchronous I/O, disk error printing, and GPT initialization.

Notable risks:
- MBR verification is intentionally weak and does not perform full overlap validation.
- Geometry inference is legacy CHS heuristic code and may only be diagnostic for modern LBA media.
- Extended partition parsing is bounded by recursion depth and `MAX_SLICES`; extra logical partitions are reported/dropped.
