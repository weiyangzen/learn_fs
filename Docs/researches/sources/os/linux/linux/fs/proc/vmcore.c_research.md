# File Research: sources/os/linux/linux/fs/proc/vmcore.c

## Role

Implements `/proc/vmcore`, the crash-dump file exposing the previous kernel's memory as an ELF core image to crash dump tools. It parses the crash kernel's ELF core header, normalizes PT_NOTE records, maps PT_LOAD memory ranges into the synthetic vmcore file, supports read and mmap access, and allows optional device dump/device RAM extensions.

## Key Mechanisms

- Maintains `vmcore_list`, a list of old-memory physical ranges with synthetic file offsets.
- Reads old memory through `read_from_oldmem()`, using `copy_oldmem_page()` or encrypted oldmem copies when needed.
- Uses SRCU-protected `vmcore_cb_list` callbacks so drivers can:
  - mark PFNs as non-RAM via `pfn_is_ram`;
  - contribute device RAM ranges when `CONFIG_PROC_VMCORE_DEVICE_RAM` is enabled.
- Exposes weak architecture hooks:
  - `elfcorehdr_alloc/free/read/read_notes`;
  - `remap_oldmem_pfn_range`;
  - `copy_oldmem_page_encrypted`.
- Supports `read_iter`, `llseek`, `open`, `release`, and MMU-only `mmap` proc operations.
- For sparse/non-RAM PFNs, reads return zeroes and mmap remaps zero pages through `remap_oldmem_pfn_checked()`.

## ELF Header Processing

- `parse_crash_elf_headers()` detects ELF32 vs ELF64 and dispatches to format-specific parsers.
- ELF sanity checks validate core type, architecture, class, version, header sizes, and program-header count.
- Multiple PT_NOTE program headers are merged into one:
  - actual note sizes are discovered by walking note headers until a zero `n_namesz`;
  - notes are copied into a vmalloc-backed buffer;
  - extra PT_NOTE program headers are removed from the exported ELF header.
- PT_LOAD entries are converted from old physical offsets to offsets in the synthetic `/proc/vmcore` file.
- `vmcore_size` is computed from adjusted ELF headers, note segment, optional device dumps, and all load ranges.

## Device Dump Support

When `CONFIG_PROC_VMCORE_DEVICE_DUMP` is enabled:

- `vmcore_add_device_dump()` validates a `vmcoredd_data` request, allocates a page-aligned buffer, writes a `NT_VMCOREDD` note header, invokes the driver's dump callback, appends the dump to `vmcoredd_list`, and updates exported ELF note/program-header sizes.
- Device dumps are placed before normal ELF notes in the exported note segment to avoid zero-filled gaps being interpreted as notes.
- Dump addition is rejected once `/proc/vmcore` is open.

## Device RAM Support

When `CONFIG_PROC_VMCORE_DEVICE_RAM` is enabled:

- callback-provided RAM ranges are converted into additional ELF64 PT_LOAD entries;
- the ELF core header buffer may be reallocated to fit new program headers;
- offsets are reset across PT_NOTE and PT_LOAD entries;
- ranges already overlapping known vmcore memory are discarded.

## Synchronization and Lifetime

- `vmcore_mutex` guards open counts, callback registration side effects, and device dump mutation.
- SRCU protects callback traversal during oldmem reads and mmap PFN validation.
- `vmcore_opened` warns about late callback or device dump changes after userspace has observed vmcore.
- `vmcore_cleanup()` removes procfs entry, frees ranges/header/note buffers, and releases device dumps.

## Research Notes

This file is the crash-dump export bridge between architecture-specific oldmem access, procfs, and ELF consumers. The security-sensitive paths are old-memory reads/mmap, sparse PFN zeroing, ELF note bounds checks, and preventing mutation of the exported file layout while userspace may be reading it.
