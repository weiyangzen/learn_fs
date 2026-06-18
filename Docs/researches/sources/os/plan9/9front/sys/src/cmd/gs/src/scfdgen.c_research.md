# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/scfdgen.c

Generator program for `scfdtab.c`, the CCITTFaxDecode lookup tables. It writes C source containing white, black, 2-D, and uncompressed decode tables.

The generator enumerates codes from the encoder tables in `scfetab.c`/`scf.h`, builds first-level and optional second-level decode nodes, fills replicated leaves for short codes, and emits extension nodes for longer codes. It also emits a dummy function for compilers requiring executable code in every source file.

Dependencies include `scf.h`, C stdio, malloc, and the CCITTFax encoding table definitions.

This is build-time table generation for stream decoding.
