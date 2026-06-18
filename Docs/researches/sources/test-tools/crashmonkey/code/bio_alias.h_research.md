# sources/test-tools/crashmonkey/code/bio_alias.h

## Purpose

`bio_alias.h` is a kernel-version compatibility shim for CrashMonkey block-device modules. It hides differences in Linux `struct bio` fields, endio APIs, discard flags, and write-operation tests behind stable macros used by `cow_brd.c` and likely `disk_wrapper.c`.

## Important APIs and Macros

- `BI_RW` maps to `bi_rw` on older kernels and `bi_opf` on newer kernels.
- `BI_DISK` maps to either `bi_bdev->bd_disk` or `bi_disk`.
- `BI_SIZE` maps to `bi_size` for older 3.12/3.13 kernels and `bi_iter.bi_size` for later kernels.
- `BI_SECTOR` maps to `bi_sector` or `bi_iter.bi_sector`.
- `BIO_ENDIO(bio, err)` abstracts the signature change from `bio_endio(bio, err)` to `bio_endio(bio)`.
- `BIO_IO_ERR(bio, err)` abstracts error completion between `bio_endio(bio, err)` and `bio_io_error(bio)`.
- `BIO_DISCARD_FLAG` maps from `REQ_DISCARD` to `REQ_OP_DISCARD`.
- `BIO_IS_WRITE(bio)` maps from `bio_rw(bio) & REQ_WRITE` to `op_is_write(bio_op(bio))`.

## Control Flow

The file is entirely preprocessor control flow. It selects one macro block based on `LINUX_VERSION_CODE` ranges: 3.12-3.13, 3.16 or 4.1, 4.4, 4.8-4.9, selected 4.14-4.16 and 5.5/5.6 patch ranges. Any other kernel version hits a compile-time `#error`.

## State and Persistence Behavior

There is no runtime state. Persistence is compile-time ABI selection: the chosen macro expansion is compiled into kernel modules and determines how they access bios and signal completion.

## Dependencies and Integration Points

The header depends on `<linux/version.h>` and is included by `cow_brd.c`. Its macros are used in `brd_make_request` for disk lookup, sector/size access, write/discard checks, and bio completion. The Makefile's kernel-version logic complements this header but does not replace its compile-time checks.

## Risks and Edge Cases

- Supported kernel ranges are sparse. Kernels outside tested patch windows fail to compile even if their APIs are compatible.
- Some ranges are patch-specific, especially 5.5.0-5.5.2 and 5.6.0-5.6.6, which suggests local compatibility fixes rather than general modern-kernel support.
- Macro abstraction can hide semantic differences, especially discard operation checks before and after `REQ_OP_*`.
- Error completion behavior differs by kernel generation; using the wrong branch can silently report successful I/O or double-complete a bio.

## Test Signals

The primary signal is successful module compilation against each supported kernel range. Runtime signals include correct write/read/discard behavior through `cow_brd`, no bio completion warnings, and correct rejection of unsupported kernels through the explicit `#error`. Compile tests should include at least one old `bi_rw` kernel and one newer `bi_opf`/`bi_disk` kernel.
