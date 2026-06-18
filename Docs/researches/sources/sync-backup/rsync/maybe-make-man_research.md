# sources/sync-backup/rsync/maybe-make-man

## Purpose
`maybe-make-man` is a build helper that converts one markdown manpage source into generated output when the Python markdown conversion stack works, or falls back to copying a prebuilt manpage where available.

## Important APIs, Types, and Functions
This is a POSIX shell script with no functions. Its inputs are one `NAME.NUM.md` argument, `md-convert`, `rsync-ssl.1.md` as a probe input, and flag files `.md2man-works` and `.md2man-force`.

## Control Flow
The script validates it received exactly one argument, derives `srcdir`, and checks for `.md2man-works`. If the flag is absent, it runs `md-convert --test` against the small `rsync-ssl.1.md` page. Success creates `.md2man-works`. Failure attempts to use an already-generated manpage in the current directory or source directory. If no fallback exists, it exits successfully only for the Samba build farm compatibility file `$HOME/build_farm/build_test.fns`; otherwise it exits with failure. If `.md2man-force` exists, it passes `--force-link-text`; then it invokes `md-convert` on the requested source file.

## State and Persistence
The script persists `.md2man-works` after a successful converter probe and may copy prebuilt manpages into the current build directory. It writes generated files indirectly through `md-convert`.

## Dependencies and Integration Points
It depends on `/bin/sh`, `dirname`, `basename`, `cp -p`, `touch`, and the adjacent `md-convert` script. It integrates with rsync's build system to avoid hard failing when optional Python markdown dependencies are unavailable.

## Risks
The probe result is cached, so dependency changes after `.md2man-works` is created are not rechecked unless the file is removed. Fallback behavior can hide converter problems if stale prebuilt output exists. The build-farm compatibility exception intentionally suppresses a real generation failure.

## Test Signals
Tests should cover successful converter probing, cached flag reuse, forced link-text option, fallback copy from current directory, fallback copy from source directory, missing fallback failure, and the Samba build-farm nonfatal path.
