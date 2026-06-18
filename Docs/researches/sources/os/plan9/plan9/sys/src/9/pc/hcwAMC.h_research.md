# File Research: sources/os/plan9/plan9/sys/src/9/pc/hcwAMC.h

- Size/hash: 2027 lines, 166004 bytes, SHA-256 `9fe944e6fed78605d6ebbbfda171ef1cb815edfefa52f994bd154f51cec8d670`.
- Purpose: Defines one static byte array, `static uchar hcwAMC[]`, containing 32385 hex byte literals. There are no functions, macros, structs, comments, or conditional sections.
- Integration: Included by `sources/os/plan9/plan9/sys/src/9/pc/devtv.c`, where `kfirloadu(tv, hcwAMC, sizeof hcwAMC)` loads the blob into the TV/video hardware path.
- Behavior: This is firmware or microcode-style data, not executable C control flow. The source file’s behavior is entirely determined by consumers that pass the byte buffer to a device loader.
- Dependencies: Relies on the including translation unit to have defined `uchar`.
- Research notes: Treat as a hardware payload asset for the Plan 9 PC TV driver. It is not filesystem-facing except as part of the broader kernel source tree inventory.
