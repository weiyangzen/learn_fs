# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/space_reftree.h

This header declares a small AVL-backed reference-counted space-range helper.

Core definitions:
- `space_ref_t` stores an AVL node, range boundary offset, and signed reference-count delta.

Public API surface:
- Create/destroy a reftree AVL.
- Add a segment with a signed refcount over `[start, end)`.
- Add every segment from a `range_tree_t` with a signed refcount.
- Generate a range tree containing ranges whose accumulated reference count reaches a caller-specified minimum.

Risk-sensitive invariants:
- The structure appears to model sweep-line reference deltas at offsets, so start/end ordering and signed counts must balance.
- Generated maps depend on the caller choosing the correct `minref` threshold.
