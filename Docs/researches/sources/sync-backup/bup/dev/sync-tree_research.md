# sources/sync-backup/bup/dev/sync-tree

## Purpose
Synchronizes a destination tree to a source tree using rsync with bup-relevant metadata support where available.

## Important APIs, Types, and Functions
Uses rsync options `-aH --delete` plus optional `-A` for ACLs and `-X` for xattrs. Supports `-h`.

## Control Flow
Parses two paths, inspects rsync feature support and `OSTYPE`, tries rsync with xattrs when available, and retries without `-X` if xattr sync fails.

## State and Persistence Behavior
Mutates destination tree to match source and deletes extra destination files.

## Dependencies and Integration Points
Used by tests/dev workflows needing a reference tree copy.

## Risks and Test Signals
Risks include destructive `--delete`, platform ACL gaps, xattr failure fallback, and rsync feature output parsing. Signal is rsync exit status.
