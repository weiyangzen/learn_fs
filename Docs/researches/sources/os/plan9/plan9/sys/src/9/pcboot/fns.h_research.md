# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/fns.h

## Purpose
Bootstrap-specific function declaration header layered on top of `../pc/fns.h`.

## Main Interfaces
- Declares boot, BIOS, config, directory, filesystem, PXE, random, stub, and libip helper functions.
- Declares `bootpass`, `askbootfile`, `dotini`, `readlsconf`, `mkmultiboot`, `warp64`, and related routines.

## Implementation Notes
- Bridges normal PC kernel prototypes with the reduced boot environment.
- Provides declarations for local stand-ins like `namecopen`, `readfile`, `myreadn`, and directory packaging.
- Includes a local forward declaration for `File`.

## Dependencies And Risks
- Used by C files that share code with the full kernel but need boot-specific shims.
- Prototype drift against copied PC/kernel code would create subtle build or ABI errors.
