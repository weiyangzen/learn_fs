# File Research: sources/os/bsd/netbsd-src/lib/libform/Makefile

## Purpose
Build description for NetBSD curses `libform`.

## Main Content
- Builds `LIB=form` with warning level 2.
- Adds current directory to include path.
- Optional `DEBUG_FORMS` enables debug info and `DEBUG`.
- Depends on NetBSD `libcurses`.
- Builds driver, field, form, post, internals, and built-in field type source files.
- Installs `form.h` into `/usr/include`.
- Defines extensive manpage and mlink mappings for form, field, driver, hook, option, validation, and fieldtype APIs.
- Includes standard NetBSD library and subdir make fragments.

## Integration
Part of NetBSD curses library stack.

## Risks / Notes
The Makefile includes many sources outside this work item, especially `internals.c` and built-in validators, which are required for the files in this group to link and behave correctly.
