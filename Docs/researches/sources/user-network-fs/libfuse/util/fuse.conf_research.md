# sources/user-network-fs/libfuse/util/fuse.conf

## Purpose
Default installed FUSE configuration file documenting optional administrator controls for non-root mounts.

## Important APIs, Types, And Functions
- `user_allow_other` enables non-root users to request `allow_other` or `allow_root`.
- `mount_max = n` sets the maximum number of FUSE mounts, default documented as 1000.

## Control Flow
No executable flow. `fuser_conf.c` parses uncommented lines exactly enough to recognize `user_allow_other` and `mount_max = <int>`.

## State And Persistence
This file is persistent host configuration installed as `/etc/fuse.conf`. Defaults are commented, so installed behavior leaves `user_allow_other` disabled and uses compiled default mount count unless changed.

## Dependencies And Integration Points
Installed by `install_helper.sh` and the Meson install script. Read by `fusermount3` and service-mount helpers through `FUSE_CONF`.

## Risks
Whitespace matters for `mount_max = n` according to the comments and parser. Enabling `user_allow_other` broadens visibility of user mounts to other users and should be an administrator decision.

## Test Signals
Test absent file, commented defaults, uncommented `user_allow_other`, valid/invalid `mount_max`, long lines, missing newline, and permission-denied open failures.
