# File Research: sources/os/linux/linux-stable/fs/proc/vmcore.c

## Summary
Implements `/proc/vmcore`, the crash-dump file exposed by the second kernel after kdump. It parses the previous kernel's ELF core headers, normalizes note segments, maps PT_LOAD memory ranges into a synthetic file, supports read and mmap access, and optionally appends device dump notes and device RAM ranges.

## Main Responsibilities
- Maintain `vmcore_list`, a list of physical crash memory ranges and their offsets in the exported vmcore file.
- Read old kernel memory through architecture hooks, honoring encrypted-memory paths and sparse/non-RAM callbacks.
- Merge multiple ELF `PT_NOTE` segments into a single note segment for 32-bit and 64-bit ELF core headers.
- Rewrite `PT_LOAD` program header offsets so the exported file has a contiguous ELF layout.
- Provide `/proc/vmcore` open, read, llseek, release, and mmap operations.
- Register/unregister vmcore callbacks used to filter RAM PFNs or contribute device RAM.
- Optionally append vmcore device dump notes under `CONFIG_PROC_VMCORE_DEVICE_DUMP`.

## Key Interfaces
- `read_from_oldmem()` copies page-aligned slices from the crashed kernel's memory, zeroing pages rejected by `pfn_is_ram()`.
- Weak architecture hooks include `elfcorehdr_alloc()`, `elfcorehdr_free()`, `elfcorehdr_read()`, `elfcorehdr_read_notes()`, `remap_oldmem_pfn_range()`, and `copy_oldmem_page_encrypted()`.
- `read_vmcore()` delegates to `__read_vmcore()` to read ELF headers, merged notes/device dumps, and memory ranges.
- `mmap_vmcore()` maps the vmcore file into userspace when `CONFIG_MMU` is available.
- `register_vmcore_cb()` and `unregister_vmcore_cb()` manage SRCU-protected callback entries.
- `vmcore_add_device_dump()` appends a driver-provided ELF note payload when device dumps are enabled.

## Important Behavior
The file layout starts with copied ELF headers, then the merged note segment, then each aligned crash memory range. During parsing, each original `PT_LOAD` `p_offset` is treated as the source physical address and replaced by the corresponding offset in the exported file.

ELF note handling reads the old kernel's note sections, calculates the real note sizes by walking `Elf{32,64}_Nhdr` entries until a zero name size or a bounds violation, copies note payloads into `elfnotes_buf`, and collapses all `PT_NOTE` headers into one page-aligned `PT_NOTE`.

Device dump notes are inserted before the original notes inside the merged note segment to avoid zero-filled gaps that user tools might misinterpret as valid notes. Adding device dumps rewrites all ELF program headers and updates `proc_vmcore->size`.

The mmap path maps ELF header pages, vmalloc-backed note/device-dump buffers, and oldmem PFNs. If callbacks exist, `remap_oldmem_pfn_checked()` replaces non-RAM pages with the zero page; on s390, the fault handler falls back to page-cache population through `__read_vmcore()`.

## State and Synchronization
`vmcore_mutex` protects open counts, callback registration side effects, and device dump list mutation. Callback traversal uses `DEFINE_STATIC_SRCU(vmcore_cb_srcu)`. `vmcore_opened` records whether userspace has opened `/proc/vmcore`, and `vmcore_open` prevents appending device dumps while the file is open.

## Cross-File Interactions
This file depends on crash-dump declarations in `include/linux/crash_dump.h`, ELF note constants from UAPI ELF headers, architecture-specific oldmem hooks, procfs registration, and optional driver callbacks that identify device RAM or non-RAM PFNs.

## Risks
Correctness depends on preserving ELF offsets after note merging and after optional device dump/device RAM insertion. Callback registration after `/proc/vmcore` has been opened is allowed but warned because the exported file may already be consumed. mmap teardown paths must unmap partially mapped ranges on failure.
