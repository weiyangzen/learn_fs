# File Research: sources/os/plan9/9front/sys/src/lib9p/share.c

## Read Status
Complete: 33 lines read.

## Purpose
Posts a 9P server and optionally advertises it through the Plan 9 share namespace.

## Main Responsibilities
- Optionally create a share directory under `#σc/<mtpt>`.
- Optionally create a share descriptor file under that directory.
- Post the service with `postsrv`.
- Write the posted fd to the share descriptor.
- Close the service fd after publishing.

## Important Function
- `postsharesrv`: posts and shares a server by name, mount point, and descriptor.

## Dependencies and Interactions
- Uses `postsrv` from `post.c`.
- Uses Plan 9 synthetic share namespace path `#σc`.
