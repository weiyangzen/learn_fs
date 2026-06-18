# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/diskload.c

## Purpose
Disk boot orchestration for `9boot`: discovers storage devices, reads partition tables, finds `9fat`/`plan9.ini`, determines a kernel, and streams it through `bootpass`.

## Main Interfaces
- Exports `bootloadproc(void*)`.
- Provides `partboot(char *path)` and internal disk/FAT boot helpers.
- Provides `dirread0`/`dirread` wrappers around device directory reads with mount/union fixups.

## Implementation Notes
- Binds `#S` into `/dev`, opens `#S`, lists disks, reads each disk ctl file, and calls `readparts`.
- `trydiskboot` initializes `#S/<disk>/9fat`, reads `plan9.ini` when present, parses it with `dotini`, reconfigures serial console, and picks `bootfile`.
- If no `bootfile` is configured, it tries to find a single `9pc`, `9k8`, or `9k10` kernel in the FAT root; otherwise it tries a raw `kernel` partition and finally prompts.
- `trybootfile` accepts `disk!part!file` or `disk!part` syntax, initializes FAT as needed, and loads either from file or partition directly.
- `partboot` streams raw partition bytes to `bootpass`.
- `bootloadproc` loops through discovered disks and eventually prompts forever on failure.

## Dependencies And Risks
- Assumes `#S` storage device namespace and partition ctl format.
- `findonekernel` returns only if exactly one plausible kernel exists.
- FAT root state is global/static in places, matching a simple one-boot-at-a-time model.
