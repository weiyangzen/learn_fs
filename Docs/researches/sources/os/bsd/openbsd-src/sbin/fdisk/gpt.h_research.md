# File Research: sources/os/bsd/openbsd-src/sbin/fdisk/gpt.h

## Purpose
Declares GPT operations and GPT global state for `fdisk`.

## Key Contents
- Prototypes for read, recovery, field prompts, initialization, write, header zapping, and printing.
- Exposes `gmbr`, `gh`, and `gp`.
- Defines GPT selection constants: `ANYGPT`, `PRIMARYGPT`, `SECONDARYGPT`.
- Defines verbosity constants: `TERSE`, `VERBOSE`.
- Defines initialization mode constants: `GHANDGP`, `GPONLY`.

## Notes
This header is consumed by command, driver, and MBR code to coordinate GPT/MBR transitions.
