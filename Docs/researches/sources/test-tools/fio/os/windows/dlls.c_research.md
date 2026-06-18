# sources/test-tools/fio/os/windows/dlls.c

## Purpose
`windows/dlls.c` provides the Windows implementation of `os_clk_tck()` for platforms where `os.h` cannot use `_SC_CLK_TCK`. It dynamically queries and raises Windows timer resolution to derive a clock tick frequency for fio timing code.

## Important APIs, Types, and Functions
The sole exported function is `os_clk_tck(long *clk_tck)`. It dynamically loads `ntdll.dll` and resolves `NtQueryTimerResolution` and `NtSetTimerResolution`.

## Control Flow
If loading `ntdll.dll` or either symbol fails, it logs a debug message and uses 64 Hz as a conservative lower-bound clock frequency. Otherwise it queries minimum/maximum/current timer resolution, requests the maximum resolution, and computes ticks per second as `10000000 / maxRes` because Windows timer resolution units are 100 ns.

## State and Persistence
The function can change process/system timer resolution through `NtSetTimerResolution()`. It does not store the loaded module handle or restore prior resolution.

## Dependencies and Integration Points
It depends on Windows dynamic loading APIs and fio debug logging. `os.h` declares `os_clk_tck()` externally when `_SC_CLK_TCK` is not available, and timing/statistics code consumes the resulting frequency.

## Risks and Edge Cases
Using maximum timer resolution may have system-wide power/performance effects. Failure fallback is coarse. The library handle is not freed, which is usually acceptable for process lifetime but worth noting. Undocumented NT APIs can change behavior across Windows versions.

## Test Signals
Windows timing initialization tests, fallback behavior with mocked missing symbols, sanity checks that `clk_tck` is nonzero, and verification that high-resolution timing improves without destabilizing long fio runs are useful.
