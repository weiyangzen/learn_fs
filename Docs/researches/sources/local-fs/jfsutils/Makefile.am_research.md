# File Research: sources/local-fs/jfsutils/Makefile.am

This is the concise handwritten Automake source for the top-level jfsutils build.

Primary behavior:
- Declares the recursive build order: `libfs include fsck fscklog logdump mkfs tune xpeek`.
- Adds `jfsutils.spec.in` to extra distribution files.
- Defines `dist-hook` to copy generated `jfsutils.spec` into the release tree.
- Defines `dist-hook` to generate `include/jfs_version.h` in the release tree with `#define JFSUTILS_DATE "<day-month-year>"`.

Important integration points:
- The subdirectory order places shared library/filesystem support and headers before tools such as `fsck`, `mkfs`, `tune`, and `xpeek`.
- The generated release header means distribution tarballs receive a build/release date without requiring the source tree to carry a static `jfs_version.h`.

Portability/build observations:
- This file is the authoritative source for the top-level recursive layout.
- The `date +%d-%b-%Y` output is locale-sensitive because `%b` depends on locale month abbreviations.
- The generated `jfs_version.h` is created only during distribution packaging, not normal local builds.
