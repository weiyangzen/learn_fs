# File Research: sources/local-fs/ocfs2-tools/install-sh

## Purpose

Portable `install-sh` script for installing files or creating directories during builds on systems without a suitable `install` command.

## Main Contents

- X Consortium/FSF-derived shell script compatible with BSD-style install behavior.
- Supports installing one or more source files to a destination file/directory or creating directories with `-d`.
- Options include copy instead of move (`-c`), group/owner/mode changes, stripping, basename/transform handling, help, and version output.
- Allows command overrides via environment variables such as `CHMODPROG`, `CPPROG`, `MKDIRPROG`, and `STRIPPROG`.
- Creates missing destination directory components manually, installs through temporary files, applies ownership/group/strip/mode, then atomically renames into place where possible.
- Cleans temporary files via traps.

## Dependencies and Integration

- Used by the build/install system generated around autotools-era portability expectations.

## Research Notes

- Script installs one file at a time despite accepting multi-source-to-directory form.
- Default behavior moves source unless `-c` is supplied.
