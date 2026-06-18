# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/Makefile.inc

## Purpose
OpenBSD make include fragment that adds the libunbound validator source directory and validator source files to the `unwind` build.

## Contents
- Sets `.PATH` to `${.CURDIR}/libunbound/validator`.
- Appends validator C files to `SRCS`.

## Source List
Includes trust anchor, key cache, key entry, negative proof/cache, DNSSEC algorithm/signature utility, and main validator files:
`autotrust.c`, `val_anchor.c`, `val_kcache.c`, `val_kentry.c`, `val_neg.c`, `val_nsec.c`, `val_nsec3.c`, `val_secalgo.c`, `val_sigcrypt.c`, `val_utils.c`, and `validator.c`.

## Integration
This file is build-system glue only. It has no runtime behavior, but it determines which validator implementation files are compiled into OpenBSD's `sbin/unwind` libunbound copy.
