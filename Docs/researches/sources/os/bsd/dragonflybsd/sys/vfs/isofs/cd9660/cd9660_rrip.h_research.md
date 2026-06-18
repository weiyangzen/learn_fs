# File Research: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_rrip.h

## Scope

Defines packed SUSP and Rock Ridge record layouts consumed by the CD9660 RRIP parser.

## Data Structures And Constants

- `ISO_SUSP_HEADER` is the common two-character type, length, and version header.
- Defines RRIP records for POSIX attributes (`PX`), device numbers (`PN`), symbolic links (`SL` and components), alternate names (`NM`), child/parent links (`CL`/`PL`), relocated directories (`RE`), timestamps (`TF`), identifier flags (`RR`), extension references (`ER`), offset/skip (`SP`), and continuation (`CE`).
- Defines component flags for current, parent, root, volume root, host, and continuation.
- Defines timestamp form and field-bit constants for create, modify, access, attribute, backup, expire, and effective times.

## Dependencies

Relies on `ISODCL()` from `iso.h` to express exact on-disk byte spans without native structure padding assumptions.

## Risks And Invariants

These structs describe on-disk byte layouts, not naturally aligned host records. Callers must use ISO numeric conversion helpers rather than direct integer reads. Variable-length fields such as symbolic-link components and alternate names require length validation by parser code.
