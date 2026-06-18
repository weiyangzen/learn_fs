# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fputwc.c

Read completely: 100 lines.

This file implements `fputwc` and `__fputwc_unlock`. It sets wide orientation, resets pending ungetwc state, converts one wide character to multibyte with `wcrtomb`, and writes the resulting bytes through `__sfvwrite`.

Important interactions: used by `fputws` and wide output paths.

Security/reliability notes: conversion failure returns WEOF with `EILSEQ`; missing wide I/O state returns WEOF with `ENOMEM`.
