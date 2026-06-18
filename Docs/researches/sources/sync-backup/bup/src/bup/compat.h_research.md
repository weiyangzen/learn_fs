## sources/sync-backup/bup/src/bup/compat.h

Purpose: declares compatibility entry points used by the native launcher.

Important APIs: exposes `int bup_py_bytes_main(int argc, char **argv);`. Actual use is gated in `bup.c` for Python 3.7.

State and risks: no state. Header is intentionally tiny; mismatches with `compat.c` would break old-Python builds.
