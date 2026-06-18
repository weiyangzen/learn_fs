# File Research: sources/os/plan9/9front/sys/src/lib9p/uid.c

## Read Status
Complete: 33 lines read.

## Purpose
Provides simple permission checking for lib9p tree-backed files.

## Important Function
- `hasperm`: checks requested access bits against other, owner, and group permission bits.

## Behavior
- Starts with “other” permissions.
- Adds owner bits if `uid` matches `f->uid`.
- Adds group bits if `uid` matches `f->gid`.
- Assumes each user is the leader of their own group, as noted in the file comment.

## Dependencies and Interactions
- Used by `srv.c` to validate open, create, and remove behavior on tree-backed fids.
