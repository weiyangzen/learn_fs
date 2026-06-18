# File Research: sources/windows/reactos/ntoskrnl/mm/i386/procsup.c

## Purpose

`procsup.c` provides the newer ARM3 i386 process address-space setup helper. It maps the new process page directory and hyperspace page through a temporary system PTE, installs required self-mappings and working-set mappings, copies kernel PDEs, and links the process into the memory-manager process list.

## Main Contents

- `MiArchCreateProcessAddressSpace(Process, DirectoryTableBase)`:
  - Extracts the page-directory PFN and hyperspace PFN from the supplied directory table base.
  - Reserves one system PTE for temporary mappings.
  - Maps the hyperspace page and writes the working-set-list PTE.
  - Remaps the same system PTE to the process page directory.
  - Copies kernel mappings from the current kernel PDE range into the process page directory.
  - Installs hyperspace and recursive PTE-base mappings.
  - Releases the temporary system PTE.
  - Inserts the process into `MmProcessList` under the expansion lock.

## Behavior And Data Flow

The function uses a single reserved system PTE as a temporary window. It first maps the hyperspace page to initialize the process working-set list entry, then remaps the window to the page directory and writes kernel, hyperspace, and recursive page-table entries. The recursive mapping makes the process page directory visible as page tables under `PTE_BASE`.

## Concurrency And Invariants

- Fails early if `MiReserveSystemPtes` cannot allocate a temporary PTE.
- Marks temporary kernel PTEs dirty and invalidates the temporary mapping after changing it.
- Uses `MiAcquireExpansionLock`/`MiReleaseExpansionLock` to update `MmProcessList`.
- Assumes `DirectoryTableBase[0]` and `[1]` already contain valid page-directory and hyperspace page frame addresses.

## Notable Details

- This file is short but important glue between architecture-specific address-space layout and generic ARM3 process management.
- Unlike `pagepae.c`, it does not allocate the page-directory pages itself; it consumes the directory-table base passed in by higher-level setup code.
