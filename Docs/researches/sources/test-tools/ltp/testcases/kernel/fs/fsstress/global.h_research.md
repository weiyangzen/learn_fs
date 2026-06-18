# sources/test-tools/ltp/testcases/kernel/fs/fsstress/global.h

## Purpose

`global.h` centralizes feature defines, XFS compatibility selection, and common system includes for `fsstress`.

## Important APIs, Types, and Functions

It defines `_GNU_SOURCE`, includes `xfscompat.h` when `NO_XFS` is set, otherwise includes `<xfs/libxfs.h>` and `<attr/attributes.h>`, and imports common POSIX/Linux headers plus `lapi/fcntl.h`.

## Control Flow

There is no runtime control flow; preprocessing chooses the XFS or non-XFS compatibility surface for `fsstress.c`.

## State and Persistence Behavior

The header owns no runtime state. It shapes compile-time visibility of types, constants, and syscall wrappers.

## Dependencies and Integration Points

Integrated directly by `fsstress.c`. The `NO_XFS` build path is selected by the local Makefile; the non-`NO_XFS` path requires XFS and attr development headers.

## Risks and Edge Cases

The include guard closes before the trailing `MAXNAMELEN`, `struct dioattr`, `MIN`, and `MAX` definitions supplied by `xfscompat.h`, so those trailing definitions are not protected if the header is included more than once through unusual paths. It also duplicates `<stdlib.h>`.

## Test Signals

Compile success in both `NO_XFS` and XFS-enabled configurations is the main signal. Include-order failures or duplicate macro/type warnings would point to guard issues.
