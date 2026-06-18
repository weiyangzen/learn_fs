# File Research: sources/os/linux/linux-stable/fs/btrfs/uuid-tree.h

## Scope

This header declares the Btrfs UUID tree public interface.

## APIs

- Declares add/remove operations for UUID/subvolume-ID mappings.
- Declares overflow checking before adding another mapping.
- Declares full-tree validation/iteration, UUID tree creation, and the UUID scan kthread entry point.

## Dependencies And Role

- Forward-declares transaction and filesystem structures.
- Used by ioctl, root/subvolume, mount, and UUID tree setup paths that need to maintain or rebuild UUID mappings.

## Risks And Invariants

- Callers must pass the correct UUID key type; the implementation only validates recognized types during iteration/checking paths.
- Add/remove require an active transaction handle.
