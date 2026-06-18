# File Research: sources/os/bsd/freebsd-src/sys/sys/physmem.h

This header declares early physical memory configuration helpers. It allows machine/platform code to add hardware RAM regions, add exclusion regions, query available/all physical memory tables, initialize global `dump_avail` and `phys_avail`, print tables, and test whether a physical range is excluded.

Exclusion flags distinguish no-dump and no-alloc regions. The comments explain the intended boot flow: collect hardware regions and exclusions in any order, then call `physmem_init_kernel_globals()` once early initialization is complete so the generated arrays communicate usable RAM to the rest of the kernel.

When `FDT` is enabled, inline helpers convert arrays of `struct mem_region` into hardware or excluded regions. Filesystem relevance is indirect but foundational: VM and buffer cache behavior depend on correct physical memory availability, and crash dump exclusion affects postmortem filesystem/storage diagnostics.
