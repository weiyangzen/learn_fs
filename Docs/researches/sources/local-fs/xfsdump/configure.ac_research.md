# File Research: sources/local-fs/xfsdump/configure.ac

## Role

This is the Autoconf input for configuring the xfsdump build.

## Package Setup

It initializes package metadata as `xfsdump` version `3.3.0`, requires Autoconf 2.50, sets auxiliary and macro directories, selects `common/main.c` as a source probe, generates `include/config.h`, and defaults prefix to `/usr`.

## Feature Options

It defines configure options for:

- shared library use
- gettext support
- lib64 support

It avoids appending `64` when the configured library directory already ends in `lib64`.

## Install Directories

It chooses root install directories. For default `/usr`-style installs, important tools go to `/sbin` and root libraries to `/<base_libdir>`. Nonstandard prefixes use normal `sbindir` and `libdir`.

## Localization

It builds `LOCALIZED_FILES` by finding all `.c` files under the source tree and substituting them for localization tooling.

## Dependency Checks

The script uses package macros to require or check:

- UUID headers and uuid compare
- pthread headers and mutex initialization
- ncurses headers and working ncurses
- XFS headers and file-handle support
- attribute headers/macros and libattr attrget
- `fallocate`
- manual page format

## Output

It generates `include/builddefs`.
