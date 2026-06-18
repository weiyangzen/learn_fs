# sources/distributed-fs/tahoe-lafs/misc/build_helpers/test-osx-pkg.py

## Purpose

This package test unpacks a macOS `.pkg` archive and verifies that `bin/tahoe --version-and-path` resolves packaged dependencies from the extracted app tree, except for a small set allowed from the OS installation.

## Important APIs, Types, and Functions

`test_osx_pkg(pkgfile)` is the main reusable function. It creates a temp directory, runs `xar`, extracts `Payload` through `gunzip` and `cpio`, runs `bin/tahoe --version-and-path`, then applies `PKG_VER_PATH_RE` to dependency lines. The script entry point selects the single `*-osx.pkg` in the current directory.

## Control Flow

Failures raise exceptions or exit nonzero. The temp directory is removed in `finally` after package extraction and command validation. Dependency path checks reject any parsed package path not under the extraction directory unless the package is `zope.interface`, `python`, `platform`, or `pyOpenSSL`.

## State, Dependencies, Integration, Risks, and Tests

State is temporary filesystem extraction under `/tmp`. Dependencies are macOS `xar`, `gunzip`, `cpio`, and the packaged `bin/tahoe`. Integration is the output from `build-osx-pkg.sh`. Risks include `os.chdir` side effects, no return-code checks for `gunzip`/`cpio`, regex type mismatch under Python 3 because `stdouttxt` is bytes but the regex is text, and hard-coded allowed system packages. Tests should mock subprocesses, validate cleanup, include dependency paths inside and outside basedir, and exercise missing/multiple package detection.
