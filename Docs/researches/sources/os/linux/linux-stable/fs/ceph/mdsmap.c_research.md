# File Research: sources/os/linux/linux-stable/fs/ceph/mdsmap.c

## Purpose

`mdsmap.c` decodes CephFS MDS maps and provides helper logic for selecting usable MDS ranks, destroying decoded map state, and determining whether the MDS cluster is available to serve metadata requests.

## Major Responsibilities

- Selects a random ready MDS rank with `ceph_mdsmap_get_random_mds()`, preferring non-laggy ranks first and then retrying while ignoring laggy status if no non-laggy rank is available.
- Provides decode-and-drop macros/helpers for unsupported or unneeded wire fields.
- Decodes versioned MDS map payloads into `struct ceph_mdsmap`.
- Tracks rank state, address, global id, laggy status, export targets, data pools, CAS pool, filesystem name, enabled/damaged state, laggy count, and max xattr size.
- Validates decoded filesystem name against the mount namespace.
- Handles older encodings by assigning `CEPH_OLD_FS_NAME` and disabling newer fs-enabled semantics.
- Frees all dynamic map allocations.
- Reports cluster availability based on enabled state, damaged state, laggy-active count, and at least one active rank.

## Decode Flow

- Reads mdsmap version/compat/length and core fields: epoch, client epoch, last failure, root, session timeout, autoclose, max file size, max mds, and active MDS count.
- Computes `possible_max_rank` from active and configured maximum ranks, then allocates rank info.
- Decodes active MDS info records, including global id, rank, state, address or address vector, laggy timestamp, and export targets.
- Decodes data pools and CAS pool.
- Skips many map sections the kernel client does not need directly: compat sets, metadata pool, timestamps, tableserver, inc/up/failed/stopped sets, snap policy booleans, balancer fields, standby counts, required client features, and rank masks.
- Updates `possible_max_rank` from the `in` rank set and counts laggy ranks.
- Decodes filesystem enabled/name state, damaged set, and max xattr size when present.

## Error Handling

- Allocation failure returns `ERR_PTR(-ENOMEM)`.
- Corrupt or invalid map content prints a hex dump, destroys partial state, and returns an error pointer.
- Some trailing extension decode failures fall through `bad_ext`, set the cursor to `end`, and still return the partially decoded usable map, reflecting forward-compatible skip behavior for optional extension fields.

## Research Notes

This file intentionally decodes only the MDS map fields needed by the kernel client. It is tightly coupled to request routing and session recovery in `mds_client.c`; rank state, laggy status, export targets, session timeout/autoclose, max file size, fs name, and max xattr size directly influence client behavior.
