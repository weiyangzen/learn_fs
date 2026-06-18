# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/memlist.h

Purpose: Defines the common boot/kernel memory segment list format.

Key definitions:
- `memlist_t`: doubly-linked list of address/size memory segments.
- `phys_install`: installed physical memory list, mutable as memory is added/deleted.
- x86-only `bios_rsvd`: BIOS reserved memory list.
- `address_in_memlist()` and `num_phys_pages()`.

Important detail: Readers of `phys_install` are expected to use `memlist_read_lock()`/`memlist_read_unlock()` even though those lock APIs are declared elsewhere.

Relevance to subset A: Core physical memory inventory structure.
