# File Research: sources/windows/dokany/sys/util/str.h

## Purpose
Header for Dokany kernel-mode string utilities implemented in `str.c`, plus an inline wrapper for borrowing raw buffers as `UNICODE_STRING`.

## Main Behavior
- Declares the shared prefix constants for DOS devices, volume GUID object paths, and object-manager paths.
- Declares allocation/free helpers for owned `UNICODE_STRING` objects.
- Declares deep-copy helpers for both allocated destination structs and caller-owned destination structs.
- Defines `DokanWrapUnicodeString(Buffer, Length)` inline, returning a non-owning `UNICODE_STRING` with `Length == MaximumLength`.
- Documents and declares backward and forward WCHAR search helpers.
- Declares prefix-checking helpers, drive-letter mount-point detection, and prefix replacement.

## Integration Points
- Included wherever Dokany needs path/mount string handling in kernel code.
- The inline wrapper is used by create, device, FCB, fileinfo, and string prefix replacement paths where buffers are already owned elsewhere.
- The declared helpers support mount manager integration, initialization, path parsing, stream detection, and FS control translation.

## Risks and Notes
- `DokanWrapUnicodeString()` is non-owning; consumers must not free the wrapped buffer through `DokanFreeUnicodeString`.
- The API mixes byte lengths (`UNICODE_STRING.Length`) with some offset parameters named generically, so caller discipline matters.
- Prefix checks are case-sensitive and do not perform Windows path normalization.
