# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/scfetab.c

Defines canonical CCITTFaxEncode run tables. It includes EOL codes, 1-D and 2-D uncompressed markers, pass/vertical/horizontal 2-D codes, Group 3 mixed-mode EOL variants, white termination/make-up tables, black termination/make-up tables, and uncompressed exit codes.

These tables are consumed directly by `scfe.c` and indirectly by `scfdgen.c` to generate decoder tables.

Dependencies include `scommon.h` and `scf.h`.

This is static CCITT fax Huffman metadata.
