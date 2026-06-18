# File Research: sources/os/bsd/netbsd-src/lib/libc/time/tzcode2netbsd

## Purpose
Historical shell helper for converting an extracted upstream tzcode distribution into a form suitable for NetBSD source-tree import.

## Behavior
The script defines a `NOIMPORT` list of upstream files that NetBSD did not want to import directly, including upstream makefiles, manual pages, sample data, images, and older documentation artifacts.

The actual destructive import operations are commented out:
- Removing files from `NOIMPORT`.
- Moving `tzfile.h` into NetBSD’s include tree.

Instead, the live script only prints reminders:
- Check `tzfile.h` in `../../../include`.
- Find the current upstream version in the Makefile.
- The script is no longer used for import.
- Current practice is to diff against the current version and apply patches.

## Integration
This file is documentation/process tooling rather than build code. It records an obsolete import workflow for the libc time/tzcode subtree.

## Notable Risks
If someone re-enabled the commented `rm`/`mv` lines without review, it could delete files from an extracted tzcode tree and move headers. As committed, it is non-mutating.
