# sources/distributed-fs/tahoe-lafs/misc/coding_tools/fixshebangs.py

## Purpose

This script rewrites exact `#!/usr/bin/python` shebangs to `#!/usr/bin/env python` for files named on the command line.

## Important APIs, Types, and Functions

It uses regex `^#! */usr/bin/python *$`, `allmydata.util.fileutil.ReopenableNamedTemporaryFile`, and `shutil.move`.

## Control Flow

For each file, it opens the input in universal newline mode, writes either a replacement first line or original lines to a temp file, closes it, then tries to atomically move the temp file over the target. If overwrite fails, it moves the original to `.bak` and then is expected to continue with fallback logic in the omitted continuation; the visible code highlights non-atomic fallback risk.

## State, Dependencies, Integration, Risks, and Tests

State is rewritten source files plus possible `.bak` files. Dependencies are Tahoe `fileutil` and filesystem move semantics. Risks include truncation if interrupted in fallback, no preservation of file mode metadata in the visible path, Python 2-only `"rU"`, and matching only one exact shebang shape. Tests should cover matching and nonmatching first lines, permissions, atomic move failure, and newline preservation.
