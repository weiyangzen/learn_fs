# File Research: sources/local-fs/jfsutils/fsck/fsckpfs.h

## Role

`fsckpfs.h` is a minimal header for fsck physical I/O mode constants.

## Contents

It contains:

- Include guard `H_FSCKPFS`.
- `#define fsck_READ  1`
- `#define fsck_WRITE 2`

## Usage

These constants are used by `readwrite_device()` and many caller paths in `fsckpfs.c` to choose read versus write dispatch. They are also passed into diagnostic messages so errors can report the attempted operation.

## Design Notes

The header does not declare the functions implemented in `fsckpfs.c`; those declarations appear to come from broader fsck headers such as `xfsckint.h` or local prototypes inside `fsckpfs.c`. Its only responsibility is the operation mode namespace.
