# File Research: sources/os/linux/linux-stable/fs/afs/addr_prefs.c

This file implements configurable address preferences for AFS server endpoint selection.

Major responsibilities:
- Parses commands written to `/proc/fs/afs/addr_prefs`.
- Maintains an RCU-published sorted preference list.
- Supports adding and deleting UDP IPv4/IPv6 address or subnet priorities.
- Applies current preference priorities to address lists when their version is stale.

Input grammar:
- Commands are split on whitespace up to newline.
- Supported commands are `add udp <IP>[/mask] <prio>` and `del udp <IP>[/mask>`.
- IPv6 addresses may be bracketed.
- Subnet masks default to `/32` for IPv4 and `/128` for IPv6.
- Mask zero and masks larger than the address family width are rejected.
- Only `udp` is accepted as the protocol.

Preference ordering:
- Preferences are partitioned with IPv4 first and IPv6 starting at `ipv6_off`.
- Within a family, entries are sorted by network address and subnet specificity.
- Exact matches update an existing priority.
- More specific subnet matches can be inserted before broader entries.
- The list expands by allocating a larger rounded-up flexible array, capped at 255 entries.

RCU/versioning:
- Writers take the proc file inode lock, clone the old list, apply all commands, publish with `rcu_assign_pointer()`, then release a new version with `smp_store_release()`.
- Old lists are freed with `kfree_rcu()`.
- Address lists store `addr_pref_version`; preference application is skipped if versions already match.
- Readers can use `afs_get_address_preferences()` to avoid RCU locking when the version is unchanged.

Application to endpoints:
- `afs_get_address_preferences_rcu()` walks IPv4 and IPv6 peers in an `afs_addr_list`, extracts remote socket addresses from RxRPC peers, finds the first exact/subnet preference match, and writes the priority into each address slot.
