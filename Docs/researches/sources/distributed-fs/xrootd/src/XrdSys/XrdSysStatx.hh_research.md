# sources/distributed-fs/xrootd/src/XrdSys/XrdSysStatx.hh

Purpose: abstracts Linux `statx` and legacy `stat` structures behind `XrdSysStatx` plus conversion helpers.

Important APIs/types/functions: on Linux/GNU, `XrdSysStatx` aliases `struct statx` and `HAVE_STATX` is set. Elsewhere, `XrdSysStatx` contains `stx_mask` and an embedded `struct stat`. `XrdSysStatxHelpers` provides `Stat2Statx()`, `Statx2Stat()`, timestamp conversions, and `GetSize()`.

Control flow: `Stat2Statx()` zeroes and fills statx fields on Linux, including dev/rdev major/minor and atime/mtime/ctime. On fallback platforms it copies `stat` into the embedded member and sets a basic mask. `Statx2Stat()` zeroes `stat` then conditionally copies each statx field based on mask bits; fallback copies the embedded `stat`.

State and persistence: no mutable global state; all operations are stack/buffer conversions.

Dependencies and integration: uses `<sys/stat.h>`, `<fcntl.h>`, `<sys/sysmacros.h>` on Linux, and mask constants such as `STATX_SIZE`. It lets filesystem code consume richer statx data while preserving older API compatibility.

Risks: non-Linux fallback defines only a subset of statx constants. `Statx2Stat()` intentionally leaves fields zero when mask bits are absent, which can surprise callers expecting complete `stat` data. Birth time is defined by mask constant but not converted into `struct stat` because portable `stat` has no uniform birth-time field.

Test signals: conversion round trips for regular files, devices, sparse files, timestamps with nanoseconds, partial statx masks, and fallback compilation on non-Linux targets.
