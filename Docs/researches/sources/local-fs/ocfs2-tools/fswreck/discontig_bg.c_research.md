# File Research: sources/local-fs/ocfs2-tools/fswreck/discontig_bg.c

This file injects corruption into OCFS2 discontiguous block group descriptors.

Key behavior:
- `create_discontig_bg_list()` builds a synthetic extent-list mapping for a group descriptor by splitting the group’s clusters across several records.
- `create_discontig_bg()` adds a new discontiguous inode allocation group for a slot:
  - resolves the slot inode allocator
  - allocates a cluster group
  - initializes an OCFS2 group descriptor
  - replaces the target chain head and links the previous group through `bg_next_group`
  - updates chain totals, inode clusters, inode size, and bitmap accounting
- `mess_up_discontig_bg()` verifies the volume supports discontiguous block groups, creates a fresh discontiguous group, then corrupts one requested field.

Supported corruptions:
- Bad extent-list tree depth, list count, record block range, record cluster counts, total cluster accounting through `l_next_free_rec`, and mixed list/record corruption patterns.

Integration notes:
- Uses `assert.h`, libocfs2 group initialization, allocation, and geometry helpers.
- Many corruptions deliberately make extent list cluster totals inconsistent with the group’s cluster-per-group value.
- Requires an OCFS2 volume with discontiguous block group support.
