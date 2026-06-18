# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/msvctail.mak

`msvctail.mak` is the common tail section for MSVC builds. It defines auxiliary-program build rules and common Windows system library response files.

The `ccf32.tr` target creates object/generated/binary directories and writes common C preprocessor definitions: `CHECK_INTERRUPTS`, `_Windows`, and `__WIN32__`, plus `GENOPT`. It then defines rules for building `echogs`, `genarch`, `genconf`, `gendev`, `genht`, and `geninit` with MSVC auxiliary compiler settings, including a distinct 64-bit `genarch` link path.

The `LIBCTR` target writes `libc32.tr`, listing standard Windows libraries such as `shell32`, `comdlg32`, `gdi32`, `user32`, `winspool`, and `advapi32`.

This file assumes `TOP_MAKEFILES`, source paths, and compiler macros have already been defined. It is intentionally included late by MSVC makefiles after command variables and platform options are set.
