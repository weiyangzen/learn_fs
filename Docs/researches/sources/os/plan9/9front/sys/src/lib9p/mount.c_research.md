# File Research: sources/os/plan9/9front/sys/src/lib9p/mount.c

## Read Status
Complete: 22 lines read.

## Purpose
Provides a convenience function to post a 9P server and optionally mount it.

## Main Responsibilities
- Call `postsrv` to create a pipe-backed server endpoint.
- Mount the returned fd at a mount point with `amount`.
- Close the service fd when no mount point is supplied.

## Important Function
- `postmountsrv`: posts `Srv` under an optional `/srv` name and mounts it at `mtpt` with the supplied flags.

## Dependencies and Interactions
- Uses `postsrv` from `post.c`.
- Uses Plan 9 `amount`; fatal errors terminate with `sysfatal`.
