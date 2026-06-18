# File Research: sources/os/linux/linux/fs/afs/addr_prefs.c

Purpose: implements address preference parsing, procfs updates, and applying priority preferences to server address lists.

Key interfaces:
- `afs_proc_addr_prefs_write()`: handles writes to `/proc/fs/afs/addr_prefs`.
- `afs_get_address_preferences()` and `_rcu()`: apply preference priorities to an `afs_addr_list`.

Implementation notes:
- Input commands are whitespace-split by `afs_split_string()` and support:
  - `add udp <IP>[/mask] <priority>`
  - `del udp <IP>[/mask]`
- Address parser accepts IPv4, IPv6, bracketed IPv6, and subnet masks; zero-length masks and oversized masks are rejected.
- Preferences are sorted by family and address/subnet order; IPv4 entries precede IPv6 entries, tracked by `ipv6_off`.
- Exact match updates existing priority; subnet match inserts tighter prefixes ahead of broader ones.
- Updates copy the old RCU-published list, mutate the copy under inode lock, increment version, publish with `rcu_assign_pointer`, and release the version with `smp_store_release`.
- Address lists cache the last applied preference version to avoid repeated scans.

Dependencies:
- Procfs seq-file network namespace lookup, RCU, RxRPC remote address access, and release/acquire memory ordering.

Edge cases:
- Preference count is capped at 255.
- The inner matching loops break only from switch cases, not the surrounding loop, so later preferences may still be inspected after a match; the final observed behavior depends on sorted ordering.
