# File Research: sources/local-fs/ocfs2-tools/libo2dlm/Makefile

## Purpose

Build rules for the static O2DLM support library.

## Main Contents

- Builds `libo2dlm.a` from `o2dlm.c`, `capabilities.c`, and generated `o2dlm_err.o`.
- Adds `-fPIC` and includes local/top-level headers.
- Conditional `HAVE_FSDLM` define.
- Optional debug executable support following the same pattern as libo2cb.
- If system libdlm headers are not found, generates `libdlm.h` symlink to `libdlm-compat.h`.
- Generates `o2dlm_err.c` and `o2dlm_err.h` from `o2dlm_err.et`.
- Provides `o2dlm_test` target and clean rules.

## Dependencies and Integration

- Produces library used for userspace DLM locking support and dlmfs capability queries.
