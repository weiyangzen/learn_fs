# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_capability.c

## Purpose
Implements Capsicum capability-rights manipulation helpers shared by the kernel and libc.

## Main Elements
- Kernel-only exported constant rights objects, such as `cap_read_rights`, `cap_write_rights`, `cap_ioctl_rights`, socket rights, pathname-operation rights, and `cap_no_rights`.
- `right_to_index()`: maps a right's encoded index bit to the corresponding `cap_rights_t` array slot.
- Varargs helpers:
  - `cap_rights_vset()` ORs rights into a rights set.
  - `cap_rights_vclear()` clears rights while preserving index/version bits.
  - `cap_rights_is_vset()` checks whether all requested rights are present.
- Public APIs:
  - `__cap_rights_init()`, `__cap_rights_set()`, `__cap_rights_clear()`, `__cap_rights_is_set()`.
  - `cap_rights_is_empty()` and `cap_rights_is_valid()`.
  - `cap_rights_merge()`, `cap_rights_remove()`, and userland `cap_rights_contains()`.

## Dependencies And Integration
Includes `<sys/capsicum.h>` and is compiled in both kernel and libc contexts. Kernel builds map `assert()` to `KASSERT()` and export preinitialized common rights values.

## Risk Notes
The rights representation encodes version, array size, and index bits inside each slot, so all bit operations must preserve metadata while modifying only rights bits. Varargs lists are terminated by a zero right; missing termination would read past arguments. Validation is strict about version, array size, index-slot consistency, and containment within all valid rights.
