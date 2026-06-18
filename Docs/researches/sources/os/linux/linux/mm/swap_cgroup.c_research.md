# File Research: sources/os/linux/linux/mm/swap_cgroup.c

## Purpose
Tracks the memory cgroup id associated with swap entries. It stores compact per-swap-slot cgroup IDs so swap accounting can identify the charged memcg after a folio has been swapped out.

## Main Interfaces
- `swap_cgroup_record()` records one folio’s cgroup id across its swap entries.
- `swap_cgroup_clear()` clears and returns the old id across a range.
- `lookup_swap_cgroup_id()` reads the id for one swap entry.
- `swap_cgroup_swapon()` allocates the per-swap-device map.
- `swap_cgroup_swapoff()` frees the map.

## Control Flow
Each `struct swap_cgroup` is an `atomic_t` packing multiple `unsigned short` ids. Lookup shifts and masks the packed word. Updates use an atomic compare-exchange loop so two ids sharing the same packed word can be changed safely.

Swapon allocates a zeroed vmalloc map sized for the swap area, then publishes it under `swap_cgroup_mutex`. Swapoff clears the pointer under the same mutex and vfree’s the map.

## State And Synchronization
State is held in `swap_cgroup_ctrl[MAX_SWAPFILES]`. Packed id updates are atomic; map pointer publication/removal is mutex-protected. Functions become no-ops or return zero when memcg is disabled.

## Dependencies
Depends on memcg swap accounting, `swp_type()`/`swp_offset()` from swapops, vmalloc allocation, and swapfile lifecycle hooks.

## Risks And Review Focus
- `swap_cgroup_record()` assumes entries for the folio were not already charged and asserts old ids are zero.
- `swap_cgroup_clear()` assumes all entries in the cleared range share the same id.
- ID width is `unsigned short`, so it depends on memcg id allocation fitting that representation.
