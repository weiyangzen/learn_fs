# sources/test-tools/stress-ng/stress-tlb-numa.c

## Purpose
Implements the `tlb-numa` stressor, a memory/TLB workload that combines CPU affinity changes, NUMA `mbind()` calls, pageout advice, shared mappings, and pthreads to provoke TLB shootdowns and inter-processor interrupts on NUMA-capable systems.

## Important APIs, Types, And Functions
`stress_tlb_numa_t` holds page size, mapping size, page pointer arrays, bogo lock, args, CPU count, NUMA masks, NUMA node mask, and option flags for disabling mbind or pageout. `stress_tlb_numa_shuffle_pages()` randomizes page traversal order. `stress_tlb_numa_change_cpu()` changes process/thread affinity to a random configured CPU and yields. `stress_tlb_numa_mmap()` wraps retrying `mmap()` and disables huge pages. `stress_tlb_numa_mbind()` optionally binds selected pages to a NUMA node. Three pthread bodies perform cross-page mbind/pageout, temporary mmap/pageout/munmap, and fragmented unmapping patterns.

## Control Flow
The entry point resolves `tlb-numa-entries`, optionally using detected x86 DTLB entries, scales entries per stressor instance, allocates two page pointer arrays and several NUMA masks, then maps two shared anonymous regions sized at two pages per TLB entry. It fills pages with non-identical data, unmaps every odd page, stores even-page addresses, shuffles both arrays, reports memory use, and starts three pthread workers. After sync it records starting TLB shootdown/IPI counters and loops mapping two temporary pages, touching them, changing CPU, optionally binding them to the next NUMA node, optionally pageout-advising them, and unmapping. After stop it records end counters, emits TLB shootdowns/sec and IPIs/sec when positive, cancels pthreads, unmaps fragmented pages, destroys the lock, and frees NUMA masks and arrays.

## State And Persistence Behavior
State is transient heap data, shared anonymous mappings, pthreads, NUMA masks, CPU affinity, and the bogo lock. No files persist. CPU affinity changes are per process/thread and end when the worker exits. NUMA page policy applies only to the temporary mappings.

## Dependencies And Integration Points
The implemented path requires `sched_setaffinity`, pthreads, and `__NR_mbind`; it includes NUMA, affinity, CPU cache, interrupt, mmap, OOM, and pthread helpers. Options are `tlb-numa-entries`, `tlb-numa-nombind`, and `tlb-numa-nopageout`. It registers as `CLASS_TLB | CLASS_MEMORY` with `VERIFY_NONE`.

## Risks And Test Signals
Systems without usable NUMA masks or mbind support skip. Thread cancellation happens without joining, which is acceptable for process teardown but means cleanup relies on cancellation points or process exit. High entry counts can allocate large shared mappings and pointer arrays. Test signals are memory usage reporting, positive TLB shootdown/IPI metrics on capable kernels, bogo progress via the shared lock, and clean no-resource skips for allocation or NUMA discovery failures.
