# File Research: sources/os/plan9/9front/sys/src/cmd/aux/na/na.h

`na.h` declares the patch metadata used by the NCR53c8xx script assembler and a `na_fixup` interface. A patch records a longword offset and an 8-bit type.

`na_fixup` accepts a script image, physical addresses for script and register space, the patch array and count, plus an external-value callback. The header is a small shared contract between generated assembler output and runtime fixup code elsewhere.
