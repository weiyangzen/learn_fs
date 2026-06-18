# File Research: sources/os/linux/linux-stable/fs/proc/kcore.c

Implements `/proc/kcore`, an ELF core-file view of kernel virtual memory.

Key points:
- Maintains `kclist_head` of memory ranges with types such as RAM, vmalloc, vmemmap, text, and user.
- Computes ELF header, program header, note, and data offsets dynamically.
- Builds ELF notes for PRSTATUS, PRPSINFO, TASKSTRUCT, and VMCOREINFO.
- Updates RAM mappings on memory hotplug through a notifier and `kcore_need_update`.
- Uses a percpu rwsem to protect the kcore range list.
- `read_kcore_iter()` streams ELF metadata and memory contents, zero-filling holes or unsafe pages.
- Avoids unsafe reads using `copy_from_kernel_nofault()`, `vread_iter()`, PFN checks, hwpoison/offline/unaccepted checks, and architecture translation hooks.
- `open_kcore()` requires `CAP_SYS_RAWIO` and passes lockdown check `LOCKDOWN_KCORE`.
- Registers `/proc/kcore` as read-only for root and permanent.

Dependencies/contracts:
- Interacts with memory hotplug, vmalloc, memblock, sparsemem/vmemmap, lockdown, and architecture address translation.
- Security-sensitive memory disclosure surface.
