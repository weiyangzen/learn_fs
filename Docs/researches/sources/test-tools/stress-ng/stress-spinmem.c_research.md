# sources/test-tools/stress-ng/stress-spinmem.c

## Purpose

`stress-spinmem.c` implements `spinmem`, a shared-memory synchronization stressor. A parent writer and child reader spin on one shared page using 8-, 16-, 32-, 64-, or optional 128-bit loads/stores, explicit memory barriers, cache-line flushes, optional scheduling yields, optional CPU-affinity changes, and optional NUMA page migration.

## Important APIs, Types, and Functions

- `SPINMEM_READER` and `SPINMEM_WRITER` macros generate typed reader/writer functions for each supported integer width.
- `SPINMEM_MB()` combines compiler/CPU barriers, `shim_mfence()`, and optional ARM DMB SY.
- `SPINMEM_FLUSH()` flushes cache data around the shared location.
- `spinmem_funcs_t` maps method names to reader/writer function pointers.
- `stress_spinmem_change_affinity()` randomly moves a process among allowed CPUs when `--spinmem-affinity` is enabled.
- `stress_spinmem_numa()` periodically randomizes NUMA placement when `--spinmem-numa` is enabled and Linux mempolicy support exists.
- `stress_spinmem_handler()` long-jumps out on `SIGALRM` when `siglongjmp` support exists.
- `stress_spinmem()` parses options, maps the shared page, installs signal handling, forks the reader child, runs writer loops in the parent, records nanoseconds per spin write/read, kills the child, and frees affinity/NUMA state.

## Control Flow

The stressor reads boolean options for affinity, NUMA, and yield, plus a method index defaulting to 32-bit. It disables unsupported affinity or NUMA modes with informational messages. It maps one shared anonymous page, installs a `SIGALRM` long-jump handler if available, selects the reader and writer functions, synchronizes, and forks.

The child repeatedly runs the selected reader. The reader waits until slot 0 changes from the last value, writes the observed value into slot `SPINMEM_OFFSET`, flushes/barriers, and optionally yields. With affinity enabled, the child runs blocks of 1000 reads and randomly changes CPU, also periodically invoking NUMA page randomization. The parent repeatedly runs the selected writer, which increments a value, publishes it to slot 0, waits for the child to echo it in slot `SPINMEM_OFFSET`, and optionally yields. The parent measures elapsed writer duration, counts loop iterations, increments bogo operations, handles affinity/NUMA variants, restores signal handling, kills the child, reports nanoseconds per operation, unmaps memory, and releases helper state.

## State and Persistence Behavior

The only shared state is one anonymous shared mmap page. Optional NUMA masks and affinity CPU arrays are allocated and freed within the stressor. Static signal jump state is process-local. No files or persistent system settings are modified, though `sched_setaffinity()` and NUMA page migration affect the running processes and page placement.

## Dependencies and Integration Points

The file integrates with stress-ng affinity, cache flush, mmap, NUMA, signal, kill/wait, and metrics helpers. It conditionally depends on Linux mempolicy, `sched_setaffinity()`, architecture memory barriers, and `siglongjmp`. The exported stressor is `CLASS_CPU | CLASS_MEMORY | CLASS_CPU_CACHE`, `VERIFY_NONE`, with method, affinity, NUMA, and yield options.

## Risks and Edge Cases

The generated spin loops have a fixed `SPINMEM_SPINS` escape count, so they avoid infinite waits but can silently move on if the peer is delayed. There is no data-correctness verification beyond the handshake. Method selection depends on the option parser limiting the index to `spinmem_funcs`; invalid external mutation could index out of bounds. NUMA page movement and affinity changes can make timing metrics noisy by design. The signal long-jump path must avoid jumping after cleanup, so `do_jmp` is cleared before restoring the handler.

## Test Signals

Expected signals include a populated "nanoseconds per spin write/read" metric, successful runs for every compiled method, fallback messages for unsupported affinity/NUMA modes, and child termination on cleanup. Test matrices should include `--spinmem-yield`, `--spinmem-affinity` with a restricted taskset, and `--spinmem-numa` on multi-node systems.
