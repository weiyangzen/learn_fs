# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/bdev_dsort.c

This file implements the classic `disksort()` seek-sort helper for block-device driver queues. It assumes the caller stores the request cylinder number in `b_resid` via the local `b_cylin` macro and maintains a `struct diskhd` activity queue through `b_actf` and `b_actl`.

The algorithm is a one-way elevator scan. The queue is treated as two ascending-cylinder lists joined together: the first contains requests at or after the current cylinder, and the second contains requests that arrived after their cylinder had already been passed. An inversion in cylinder order marks the transition from the first list to the second.

If the queue is empty, the new buffer becomes both head and tail. If the new request is before the current request, `disksort()` searches for the inversion and inserts into the second list in ascending order, or appends if no larger second-list request exists. If the new request is at or after the current request, it inserts into the first list before the first larger cylinder or just before an inversion. Tail bookkeeping updates `b_actl` when insertion occurs after the old tail.

This helper depends only on legacy buf queue fields and driver-provided cylinder numbers. Its correctness depends on callers maintaining the activity queue invariant and interpreting `b_resid` as a sortable seek position.
