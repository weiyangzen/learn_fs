# File Research: sources/local-fs/ocfs2-tools/libo2cb/Makefile

## Purpose

Build rules for the static O2CB support library.

## Main Contents

- Builds `libo2cb.a` from `o2cb_abi.c`, `o2cb_crc32.c`, `client_proto.c`, and generated `o2cb_err.o`.
- Adds `-fPIC`, warning flags, and include paths for top-level includes and local headers.
- Conditional defines for CMAP, FSDLM, CMAN, and debug executable support.
- Generates `o2cb_err.c` and `o2cb_err.h` from `o2cb_err.et` using `compile_et`.
- Optional debug programs are derived from C files containing `DEBUG_EXE`.
- Man page output includes `o2cb.7`.
- Clean rules remove generated error files.

## Dependencies and Integration

- Produces the library consumed by OCFS2 tools needing cluster stack/configfs/control-daemon operations.
