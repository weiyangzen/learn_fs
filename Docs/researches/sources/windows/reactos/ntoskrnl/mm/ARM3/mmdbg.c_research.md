# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/mmdbg.c

## Role

`mmdbg.c` implements ARM3 memory-manager support for kernel debugger memory copies. It provides translation of physical addresses through a reserved debug mapping PTE and implements `MmDbgCopyMemory` for small aligned reads/writes of physical or virtual memory.

## Key mechanisms

- Maintains `MiDebugMapping` initialized to `MI_DEBUG_MAPPING` and `MmDebugPte`, which is set during memory initialization once debugger physical-memory support is ready.
- `MiDbgTranslatePhysicalAddress` rejects early calls before `MmDebugPte` is initialized, rejects cache-mode flags because cached/uncached/write-combined debug mappings are not implemented, rejects I/O-space PFNs with no PFN database entry, then writes a temporary valid kernel PTE for the requested PFN and invalidates the mapping TLB entry.
- `MiDbgUnTranslatePhysicalAddress` clears the debug PTE and invalidates the TLB entry after a physical copy.
- `MmDbgCopyMemory` supports only 1-, 2-, 4-, and 8-byte transfers, enforced by `MMDBG_COPY_MAX_SIZE == 8`, and rejects unaligned requests.
- For `MMDBG_COPY_PHYSICAL`, it maps the physical address through the debug PTE. For virtual copies, it checks `MmIsAddressValid`, notes session-space handling as a FIXME, and if a write targets a non-writable PTE, falls back to a physical write through the page frame.
- Performs typed scalar copies rather than arbitrary `memcpy`, matching the limited debugger transfer sizes.

## Dependencies and coupling

- Depends on `miarm.h` for `ValidKernelPte`, `MiPteToAddress`, `MiAddressToPte`, `MiGetPfnEntry`, `MI_IS_PAGE_WRITEABLE`, and page/TLB helpers.
- Depends on `MmDebugPte` being initialized by `MmArmInitSystem` in `mminit.c`.
- Uses `MmIsAddressValid`, declared elsewhere and implemented in `mmsup.c`, for virtual and debug mapping validation.

## Limitations and risks

- Debug cache flags are explicitly unsupported.
- Physical I/O space is explicitly unsupported because `MiDbgTranslatePhysicalAddress` requires a PFN database entry.
- Local kernel-debugger locking is not implemented; missing `MMDBG_COPY_UNSAFE` only logs once and does not change behavior.
- Session-space handling is marked incomplete.
