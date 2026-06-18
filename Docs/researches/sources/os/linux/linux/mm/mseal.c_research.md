# File Research: sources/os/linux/linux/mm/mseal.c

Implementation of the `mseal(2)` syscall, which seals VMA metadata over a fully mapped address range so later operations cannot alter the mapping layout or selected protections/contents.

Key responsibilities:
- Implements `do_mseal()` and `SYSCALL_DEFINE3(mseal)`.
- Validates flags, tagged/aligned start address, rounded length, overflow, zero-length no-op, and mmap write-lock acquisition.
- Rejects ranges that contain unmapped gaps at the start, middle, or end.
- Applies `VMA_SEALED_BIT` across all VMAs in the range, splitting/merging with `vma_modify_flags()` as needed.
- Allows repeated sealing of already sealed VMAs as a no-op.

Important behavior:
- `range_contains_unmapped()` walks VMAs from `start` to `end` and returns true if any gap exists before the next VMA or after the last VMA.
- `mseal_apply()` modifies only the overlapping portion of each VMA, updates iterator/previous VMA state, starts VMA write mode, and sets the sealed flag.
- The syscall holds mmap write lock across both validation and application so the range cannot change between the gap check and flag updates.
- Sealed VMAs are enforced by other files in this group: `mprotect.c` rejects protection changes, `mremap.c` rejects remaps, and mmap/munmap paths rely on unmap/fixed-map helpers checking seals.

Dependencies:
- VMA iterators, VMA flag modification helpers, per-VMA write locking, tagged-address handling, mmap write lock, and the shared `VMA_SEALED_BIT` semantics used by mmap/mprotect/mremap/madvise paths.

Notable risks:
- The syscall intentionally rejects ranges with holes to avoid giving callers a false sense that future mappings into holes are sealed.
- VMA modification can still fail due to splitting/merging allocation or map-count pressure.
- There is no unseal operation; setting `VMA_SEALED_BIT` is permanent for the VMA lifetime.
