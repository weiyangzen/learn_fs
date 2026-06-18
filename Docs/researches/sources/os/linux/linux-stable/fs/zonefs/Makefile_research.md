# File Research: sources/os/linux/linux-stable/fs/zonefs/Makefile

## Purpose

Defines zonefs build objects.

## Main Responsibilities

- Adds local include path.
- Builds `zonefs.o` under `CONFIG_ZONEFS_FS`.
- Links `super.o`, `file.o`, and `sysfs.o`.

## Important Invariants

- `trace.h` is included through local source include path.
- zonefs is built as a single composite object.

## Dependencies

Kernel kbuild and `CONFIG_ZONEFS_FS`.

## Research Notes

Minimal kbuild wiring for the zonefs module/filesystem.
