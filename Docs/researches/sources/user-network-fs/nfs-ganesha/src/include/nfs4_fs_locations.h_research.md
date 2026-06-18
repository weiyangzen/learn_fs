# sources/user-network-fs/nfs-ganesha/src/include/nfs4_fs_locations.h

## Purpose

`nfs4_fs_locations.h` declares lifecycle helpers for NFSv4 `fs_locations` referral/replication data stored in FSAL attributes.

## Important APIs, Types, and Functions

The API includes `nfs4_fs_locations_new(fs_root, rootpath, count)`, `nfs4_fs_locations_get_ref`, `nfs4_fs_locations_release`, and `nfs4_fs_locations_free`. The type is `fsal_fs_locations_t` from `fsal_types.h`.

## Control Flow

Export or FSAL code constructs a locations object for a root/path and server-location count, passes references through attributes, and releases references when attributes or exports are destroyed. The free function is the terminal cleanup path.

## State and Persistence Behavior

The structure is process memory with reference counting. The actual referral configuration persists in export/FSAL config or backend metadata, not in this helper.

## Dependencies and Integration Points

It integrates with NFSv4 GETATTR `fs_locations`, referrals, pseudo filesystem exports, and FSAL attribute conversion code.

## Risks and Test Signals

Risks include reference leaks across cached attributes, use-after-free on shared fs_locations, path normalization errors, and count/allocation mismatches. Tests should create zero and multi-location objects, exercise get/release from multiple owners, encode NFSv4 attributes, and reload exports carrying referrals.
