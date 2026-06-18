# sources/test-tools/stress-ng/stress-nop.c

## Purpose
`stress-nop.c` implements the `nop` CPU stressor. It burns CPU cycles by executing architecture-specific no-op or low-impact instructions in tight loops, optionally selecting a random instruction variant. It also measures approximate nanoseconds per instruction.

## Important APIs, Types, and Functions
The file exports `stress_nop_info` with `CLASS_CPU` and an option `nop-instr`. `stress_nop_instr_t` maps instruction names to generated spin functions, optional CPU feature checks, and runtime ignore state. The `STRESS_NOP_SPIN_OP` macro generates loop bodies that execute an operation 64 x `NOP_LOOPS` times per inner iteration and update duration/count metrics. Architecture-specific operations include generic `stress_asm_nop`, x86 pause/tpause/serialize and multi-byte NOPs, ARM yield, PowerPC yield/mdoio/mdoom, and s390 nopr where available. `stress_nop_random()` samples non-random entries. `stress_sigill_nop_handler()` handles illegal instruction traps with `siglongjmp`. `stress_nop()` coordinates setup, execution, and metrics.

## Control Flow
At startup the stressor reads the selected `nop-instr` method and installs a `SIGILL` handler. If an instruction traps, the longjmp path marks the current instruction ignored, skips the stressor if even generic `nop` is illegal, or falls back to generic `nop` for fixed methods. After sync start, `stress_nop_callfunc()` performs the CPU feature check on first use, falls back to generic nop when unsupported, and then runs the selected spin loop until `stress_continue(args)` fails. Random mode repeatedly selects an instruction other than `random` and invokes it for one bounded spin block. At the end it stores a harmonic mean metric for nanoseconds per nop instruction.

## State and Persistence
The static `jmp_env` and `current_instr` support signal recovery. Each instruction entry caches whether its support check has run and whether it should be ignored. Duration and count are local to one stressor invocation and only the final metric is stored in stress-ng shared stats. There is no external persistent state.

## Dependencies and Integration Points
The stressor depends on architecture-specific assembly helper headers, `HAVE_ASM_NOP`, and `HAVE_SIGLONGJMP`. Optional CPU feature probes come from `core-cpu.h`. It integrates with stress-ng settings, signal handling, sync start, bogo counters, process states, random generator, and metric reporting. Unsupported builds still expose the `nop-instr` option through an unimplemented method callback.

## Risks
Instruction availability can differ between compiler target, CPU model, virtualization layer, and runtime feature bits; the SIGILL recovery path is critical. `current_instr` is static process state and must be valid when `SIGILL` fires. Random mode can repeatedly choose unsupported instructions until their ignore flags are cached. The timing metric measures loop wall time around large batches and is affected by frequency scaling, scheduler preemption, and instruction-specific wait behavior such as `tpause`.

## Test Signals
Run `--nop 1 --timeout 1 --metrics` and each exposed `--nop-instr` method on matching architectures. On x86, cover multi-byte nop variants and feature-gated `serialize` or `tpause` when available. Negative testing can force unsupported instruction selection on hardware lacking a feature and confirm graceful fallback instead of process death.
