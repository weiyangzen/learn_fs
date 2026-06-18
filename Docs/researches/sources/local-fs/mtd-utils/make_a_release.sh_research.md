# File Research: sources/local-fs/mtd-utils/make_a_release.sh

## Purpose
Automates the mtd-utils release preparation flow: version validation, Makefile version update, signed tag creation, tarball generation, detached GPG signature, and release announcement template.

## Control Flow
The script requires `<new_ver> <outdir>`, validates `X.Y.Z` version syntax, verifies the Makefile contains a version line, rejects dirty git state and pre-existing tags, edits `VERSION = ...`, commits the change, creates a signed `vX.Y.Z` tag, archives it as `mtd-utils-X.Y.Z.tar.bz2`, signs the tarball, and prints upload/send-email instructions.

## Dependencies
Requires a clean git checkout, `sed`, `git`, `bzip2`, `gpg`, and release infrastructure access for the printed `scp` target.

## Risks and Notes
The script intentionally mutates git history by committing and tagging. It assumes the release branch is `master` in the printed push command. The error message for bad argument count contains a typo but does not affect behavior.
