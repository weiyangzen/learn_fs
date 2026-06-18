# File Research: sources/local-fs/erofs-utils/mkfs/Makefile.am

## Scope

This Automake fragment defines the `mkfs.erofs` build target.

## Build Rules Covered

- Sets `AUTOMAKE_OPTIONS = foreign`.
- Builds one program, `mkfs.erofs`.
- Adds libselinux CFLAGS to `AM_CPPFLAGS`.
- Compiles `mkfs_erofs_SOURCES = main.c`.
- Uses `-Wall` and the top-level `include` directory in `mkfs_erofs_CFLAGS`.
- Links against the in-tree `lib/liberofs.la`.

## Dependencies

- Requires the top-level Automake/libtool build to provide `liberofs.la` and configured `${libselinux_CFLAGS}`.

## Risks And Invariants

- `mkfs.erofs` is intentionally a thin target around `main.c`; most functionality is linked from `liberofs`.
- Include paths and libselinux flags must remain consistent with configuration-time feature detection.
