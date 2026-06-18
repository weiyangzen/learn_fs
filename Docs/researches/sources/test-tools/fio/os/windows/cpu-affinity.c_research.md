# sources/test-tools/fio/os/windows/cpu-affinity.c

## Purpose
`windows/cpu-affinity.c` implements fio's Windows CPU mask and affinity operations, including support for Windows processor groups on systems with more than 64 logical CPUs.

## Important APIs, Types, and Functions
Exports are `first_set_cpu()`, `fio_setaffinity()`, `fio_cpuset_init()`, `fio_getaffinity()`, `fio_cpu_clear()`, `fio_cpu_set()`, `fio_cpu_isset()`, `fio_cpu_count()`, and `fio_cpuset_exit()`. Internal helpers include `print_mask()`, `last_set_cpu()`, `mask_to_group_mask()`, and `cpu_to_row_offset()`.

## Control Flow
`mask_to_group_mask()` finds the first set linear CPU, maps it to a Windows processor group by walking active groups and counts, rejects masks spanning multiple groups, extracts a group-relative bitmask from fio's row mask, and returns group plus affinity mask. `fio_setaffinity()` opens the target thread and applies `SetThreadGroupAffinity()`. `fio_getaffinity()` opens a process, requires it to be associated with exactly one group, reads `GetProcessAffinityMask()`, and expands that group-relative mask back into fio's linear rows. Bit operations map CPU indexes to row/offset and update/test/count bits.

## State and Persistence
The module stores no global state. `fio_setaffinity()` changes thread affinity. `fio_getaffinity()` returns a snapshot in caller-provided `os_cpu_mask_t`.

## Dependencies and Integration Points
It depends on `os/os.h`, Windows group affinity APIs, fio debug logging, `hweight64()`, and the mask constants from `os-windows-7.h`. It backs the `cpumask`, `cpus_allowed`, and CPU split logic used by `options.c` on Windows.

## Risks and Edge Cases
Masks spanning processor groups are rejected because Windows thread group affinity can bind a thread to one group at a time. `fio_getaffinity()` rejects processes associated with multiple groups. The row/offset helper appears suspicious: `*offset = cpu << FIO_CPU_MASK_STRIDE * *row` looks like a shift expression where modulo/subtraction was intended, so high CPU indexes should be tested carefully. Fixed `FIO_MAX_CPUS` also limits very large systems.

## Test Signals
Unit tests for first/last set CPU, row/offset mapping at 0, 63, 64, 127, and 511, affinity set/get on single-group and multi-group hosts, rejection of cross-group masks, and hweight-based counts are important.
