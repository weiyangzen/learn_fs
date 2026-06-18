# File Research: sources/os/linux/linux-stable/fs/orangefs/orangefs-debug.h

## Scope

This header defines OrangeFS kernel debug mask constants.

## APIs And Constants

- Defines `GOSSIP_NO_DEBUG` and subsystem masks for super, inode, file, dir, utils, wait, ACL, dcache, dev, name, bufmap, cache, debugfs, xattr, init, and sysfs.
- Defines `GOSSIP_MAX_NR` and `GOSSIP_MAX_DEBUG`.

## Dependencies And Role

- Kernel builds include Linux types; userspace-compatible inclusion falls back to standard integer types and `ARRAY_SIZE`.
- Masks are consumed by debug logging and debugfs keyword conversion.

## Risks And Invariants

- Mask values must remain collision-free because debugfs maps keywords to bits.
- `GOSSIP_MAX_DEBUG` assumes all active masks fit below `GOSSIP_MAX_NR`.
