# sources/test-tools/stress-ng/stress-mmapfiles.c

Purpose: `stress-mmapfiles.c` recursively scans common system directories and mmaps many regular files read-only, then unmaps them while collecting mmap/munmap throughput and pages-per-mapping metrics. It can use shared mappings, populate pages, and randomize NUMA placement.

Important APIs/types/functions: `stress_mapping_t` stores an address/length pair. `stress_mmapfile_info_t` is shared between parent and child and contains metrics, option booleans, ENOMEM state, the mappings array, and optional NUMA masks. `stress_mmapfiles_dir` recursively maps files under a path. `stress_mmapfiles_child` drives scanning/unmapping over a fixed directory list.

Control flow: the parent maps shared info, initializes counters/options, allocates NUMA masks if requested, and runs an oomable child. The child allocates up to `MMAP_MAX` mapping slots, synchronizes, then repeatedly scans directories in rotating order (`/lib`, `/lib32`, `/lib64`, `/boot`, `/bin`, `/etc`, `/sbin`, `/usr`, `/var`, `/sys`, `/proc`). Each regular file is opened, sized, checked against OOM avoidance, mmapped read-only with private/shared/populate flags, optionally NUMA-randomized and touched for populate, recorded in the mapping table, and counted. After a scan pass, all recorded mappings are timed through `munmap` or force-unmapped.

State and persistence behavior: no files are created or modified. State is shared anonymous metric data plus a child-private heap mappings array. Mapped files are read-only; system directory traversal state is transient.

Dependencies and integration points: the file uses core mmap, NUMA, OOM, put helpers, directory type shims, memory metrics, and stress-ng metrics. It registers `CLASS_VM | CLASS_OS`, `VERIFY_ALWAYS`, and options for NUMA, populate, and shared mappings.

Risks: scanning `/proc` and `/sys` can encounter dynamic files, zero-length files, disappearing entries, and mapping failures; the code largely skips failures. Mapping huge numbers of files can hit `vm.max_map_count`, fd limits, or ENOMEM. Recursive traversal has no explicit symlink following but depends on directory type shims being accurate. Shared mapping of read-only files may behave differently across special filesystems.

Test signals: run `stress-ng --mmapfiles 1 --mmapfiles-ops 1`, repeat with `--mmapfiles-populate` and `--mmapfiles-shared`, and on NUMA systems with `--mmapfiles-numa`. Metrics should include file mmaps/munmaps per second, pages mmaped/munmapped per second, and pages per mapping.
