# File Research: sources/os/plan9/9front/sys/src/cmd/dossrv/errstr.h

## Purpose
Defines the internal error-code to string mapping for `dossrv`.

## Key Contents
- Initializes `errmsg[ESIZE]` with user-facing messages for format errors, I/O errors, authentication, memory, missing files, permission, missing filesystem, bad fcall/stat/version, long names, contiguous-space failures, and system-call errors.

## Interfaces And Dependencies
- Included by `xfssrv.c`, where `xerrstr()` maps `errno` values to 9P `Rerror` strings.

## Notes
The array is defined in the header rather than declared extern, so it is intended to be included by exactly one compilation unit.
