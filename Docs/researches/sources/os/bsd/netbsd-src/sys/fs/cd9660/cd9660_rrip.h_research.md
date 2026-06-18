# File Research: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_rrip.h

Read completely: 143 lines.

Defines the packed-ish C layouts used to interpret Rock Ridge and SUSP records embedded in ISO9660 directory records. `ISO_SUSP_HEADER` provides the common two-byte type, one-byte length, and one-byte version fields used by all parsers in `cd9660_rrip.c`.

The header covers RRIP structures for POSIX attributes (`PX`), device numbers (`PN`), symbolic links (`SL` plus `ISO_RRIP_SLINK_COMPONENT`), alternate names (`NM`), child/parent links (`CL`/`PL`), relocated directories (`RE`), timestamps (`TF`), RR flags (`RR`), extension references (`ER`), `SP` skip offsets, and continuation areas (`CE`).

It also defines component and timestamp flag constants used when constructing symlink paths and deciding whether timestamps are 7-byte ISO or 17-byte ASCII form. The structures intentionally use byte arrays and `ISODCL` ranges because ISO9660 fields are unaligned and often stored in ISO numeric encodings.
