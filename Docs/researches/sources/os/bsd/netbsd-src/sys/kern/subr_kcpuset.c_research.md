# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_kcpuset.c

Read completely: 546 lines.

Implements dynamic kernel CPU sets. A `kcpuset_t` is a variable-sized bitfield embedded after a small implementation header carrying a reference count and deferred-free chain pointer.

Core behavior:
- Early boot users receive temporary static one-word bitsets recorded by pointer; `kcpuset_sysinit()` replaces them with dynamically allocated full-size sets.
- `kcpuset_create()`, `clone()`, `destroy()`, `use()`, and `unuse()` manage allocation and references.
- Copyin/copyout bridge user `cpuset_t` data.
- Bit operations include zero/fill/copy/set/clear/test, match/intersection checks, first-set-bit, merge/intersect/remove, and population count.
- Atomic variants set/clear and merge/intersect/remove through atomic word operations.

Risks and notes:
- Early boot support is limited to `KC_SAVE_NITEMS` entries and one 32-bit word until fixup.
- Reference-counted sets must not be modified after being placed on a deferred free list.
- User copy length larger than the kernel bitfield is rejected.
