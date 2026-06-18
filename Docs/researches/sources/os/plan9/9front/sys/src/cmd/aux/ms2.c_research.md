# File Research: sources/os/plan9/9front/sys/src/cmd/aux/ms2.c

`ms2` converts either a Plan 9 executable or a raw binary file into Motorola S-record output. It uses `libmach` `crackhdr` for executable headers unless `-b` raw binary mode is selected.

Options select data segment only (`-d`), suppress end record (`-s`), set base address (`-a`), set page alignment between text/data (`-p`), halfword byte-swap (`-h`), binary input (`-b`), and S1/S2/S3 record width (`-1`, `-2`, `-3`). Records are capped at 32 payload bytes.

For executables, it emits text then page-aligns `addr` before emitting data; for raw files it emits the whole file from address 0 and writes an S9 trailer. Checksums are the standard one-byte complement of length, address, and data.
