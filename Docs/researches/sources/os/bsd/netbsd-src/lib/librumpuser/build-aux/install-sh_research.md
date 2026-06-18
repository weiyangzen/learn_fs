# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/build-aux/install-sh

Read completely: 527 lines.

## Purpose
Vendored portable `install` replacement compatible with BSD-style install usage.

## Main Responsibilities
- Supports installing one file to another, multiple files into a directory, `-t DIRECTORY`, `-T`, and directory creation with `-d`.
- Supports options for group, owner, mode, stripping, copy-on-change, and dry-run through `DOITPROG`.
- Allows command overrides through environment variables such as `CHGRPPROG`, `CHMODPROG`, `CHOWNPROG`, `CMPPROG`, `CPPROG`, `MKDIRPROG`, `MVPROG`, `RMPROG`, and `STRIPPROG`.
- Computes safe umasks for file copies and directory creation.
- Tests for working POSIX `mkdir -p` behavior and falls back to step-by-step directory creation when needed.
- Copies to a temporary file in the destination directory, applies ownership/group/strip/mode changes, optionally skips replacement when `-C` detects no content/metadata changes, then renames into place.
- Uses traps to clean temporary files on interrupt or exit.

## Filesystem Relevance
Build/install-only. It performs portable file and directory installation during builds but is not part of runtime filesystem implementation.

## Reliability Notes
- Handles old or nonconforming `mkdir`, `mv`, and shell behavior with conservative fallbacks.
- Uses temporary names based on `$$` in the destination directory; normal for this class of historical build helper, but not designed as a security boundary.

## Dependencies
- POSIX shell plus standard file utilities: `cp`, `mv`, `rm`, `mkdir`, `chmod`, `chown`, `chgrp`, `cmp`, `strip`, `ls`, `dirname`, `basename`, `expr`, `sed`.
