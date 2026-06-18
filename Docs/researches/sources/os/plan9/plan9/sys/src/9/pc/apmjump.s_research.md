# File Research: sources/os/plan9/plan9/sys/src/9/pc/apmjump.s

x86 assembly helper for protected-mode APM BIOS far calls.

Key responsibilities:
- Defines global `apmjumpstruct` containing the far-call offset and segment.
- Provides small `fortytwo` and `getcs` helpers.
- `apmfarcall(seg, off, Ureg*)` builds the far pointer, loads selected registers from `Ureg`, saves segment/general registers, installs `APMDSEG` in DS, performs an absolute far call through the jump structure, restores registers/segments, stores flags and selected returned registers back into `Ureg`, and returns carry flag status.

Important behavior:
- Explicitly warns it is not reentrant/thread-safe because it uses global jump parameters.
- Avoids using `FP` after manual stack manipulation starts.

Dependencies:
- Depends on `APMDSEG` and Ureg field offsets from PC kernel headers.

Notable risks:
- Ureg offsets are hard-coded numeric displacements.
- BIOS calls run with delicate segment state; incorrect GDT setup in `apm.c` would break this path.
