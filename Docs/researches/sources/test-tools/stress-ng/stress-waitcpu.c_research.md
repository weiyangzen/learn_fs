# sources/test-tools/stress-ng/stress-waitcpu.c

## Purpose
Implements `waitcpu`, which repeatedly executes architecture-specific wait, pause, yield, barrier, or no-op instructions and measures their rates.

## Important APIs, types, and functions
`stress_waitcpu()` is the entry point. `stress_waitcpu_method_t` maps method names, wait functions, support probes, counters, durations, and rates. Methods are compiled conditionally for generic `nop`, x86 `pause/tpause/umwait`, ARM `yield`, OpenRISC `psync`, PPC/PPC64 `yield/mdoio/mdoom`, RISC-V `pause`, and Loong64 `dbar`.

## Control flow
Startup probes all compiled methods, logs supported instructions, and skips if none are available. After synchronized start, it executes each supported method 1000 times per pass, accumulates timing/counts, and increments bogo. At exit it records per-method rates and on x86 compares non-nop rates against `nop` when not virtualized.

## State and persistence
State lives in the static method table and static adaptive delay variables for waitpkg instructions. Counts and durations are reset on start. `/proc/cpuinfo` is read only for the x86 virtualization check.

## Dependencies and integration points
Registered as `stress_waitcpu_info` with `CLASS_CPU` and `VERIFY_ALWAYS`. Depends on stress-ng architecture assembly wrappers, CPU feature probes, timing, metrics, and `/proc/cpuinfo` on x86.

## Risks and edge cases
Wait instructions are hardware and virtualization sensitive. Suspicious non-nop rates only produce an informational note. If no instruction is supported, the stressor exits `EXIT_NO_RESOURCE`.

## Test signals
Metrics report `<instruction> ops per sec`. Instance zero logs the instruction set exercised; x86 may log a sanity note when a wait instruction is faster than `nop` by more than about 50 percent.
