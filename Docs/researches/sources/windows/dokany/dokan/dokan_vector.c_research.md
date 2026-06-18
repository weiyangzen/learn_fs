# File Research: sources/windows/dokany/dokan/dokan_vector.c

Small generic dynamically-sized vector used by Dokan object pools and directory enumeration.

Key responsibilities:
- Allocates vectors with default capacity or explicit capacity.
- Frees vector items and, unless marked stack-allocated, the vector object itself.
- Supports push-front, push-front-array, push-back, push-back-array, pop-back, pop-back-array, clear, indexed lookup, last-item lookup, count, capacity, and item-size queries.
- Grows backing storage by doubling or by at least twice the requested minimum increase.

Important behavior:
- Default capacity is 128 items.
- `AllocWithCapacity(..., 0)` creates a vector with no backing allocation until it grows.
- Push-front shifts existing entries with `memmove_s`; push-back appends with `memcpy_s`.
- Pop and get functions assert their preconditions but include limited runtime fallback behavior.
- `DokanVector_Grow()` handles a zero-capacity vector and otherwise reallocates.

Dependencies:
- Includes `dokani.h` for debug printing and Windows types.
- Uses CRT allocation and secure copy/move functions.

Notable risks:
- Capacity checks use `ItemCount + Count >= MaxItems`, so a full vector grows before using the final slot; this wastes one slot but avoids boundary ambiguity.
- Multiplication for allocation sizes is not checked for overflow.
- `DokanVector_Grow(Vector, 0)` on a nonzero full vector relies on normal doubling; zero-capacity with nonzero minimum skips the first special case and still reaches default capacity.
- `IsStackAllocated` is supported in `Free()` but no initializer for stack-allocated vectors appears in this file.
