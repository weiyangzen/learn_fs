# File Research: sources/virtualization/nbd/tests/code/size.c

## Purpose
Tests `size_autodetect()` on a temporary file.

## Behavior
Creates and unlinks a temporary file, seeks to byte 1023, writes one byte, and asserts that detected size is 1024 and not 1023.

## Dependencies
Uses `mkstemp()`, `lseek()`, `write()`, `size_autodetect()`, and `macro.h`.

## Risks and Notes
The test exercises regular-file size detection, not block-device ioctl or nonseekable fallback paths.
