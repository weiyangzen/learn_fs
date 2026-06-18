# sources/test-tools/fio/os/os-windows-7.h

## Purpose
`os-windows-7.h` defines fio's Windows CPU mask shape for Windows 7 and later processor-group APIs.

## Important APIs, Types, and Functions
It defines `FIO_MAX_CPUS` as 512, `FIO_CPU_MASK_STRIDE` as 64, `FIO_CPU_MASK_ROWS` as `FIO_MAX_CPUS / FIO_CPU_MASK_STRIDE`, and `os_cpu_mask_t` as a struct containing `uint64_t row[FIO_CPU_MASK_ROWS]`.

## Control Flow
There is no runtime flow. The constants determine how `windows/cpu-affinity.c` maps linear CPU indexes into row/bit positions and Windows processor groups.

## State and Persistence
The type stores in-memory CPU masks only. It has no persistent state.

## Dependencies and Integration Points
`os-windows.h` includes this header and declares CPU affinity helpers that consume `os_cpu_mask_t`.

## Risks and Edge Cases
The hard cap of 512 logical CPUs is based on an older Hyper-V limit and may be too small for future or very large systems. All row/offset math in the implementation depends on these constants.

## Test Signals
Windows affinity tests on systems with more than 64 CPUs and compile-time checks for mask row count validate this definition.
