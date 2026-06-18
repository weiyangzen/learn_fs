# sources/test-tools/stress-ng/core-asm-x86.h

Purpose: x86 inline assembly layer for CPUID, timing, random, cache, fence, wait, prefetch, direct-store, and flags instructions.

Important APIs and control flow: provides PIC-safe `stress_asm_x86_cpuid`, locked add, pause/serialize, `rdtsc/rdtscp`, retry-loop `rdrand/rdseed`, `tpause/umwait/umonitor`, cache flush/demote/writeback/prefetch instructions, fences, `movdiri`, and `lahf`.

State and persistence: no persistent state; some helpers busy-wait until hardware random instructions report carry success and others affect cache or low-power wait behavior.

Dependencies and integration: heavily consumed by `core-cpu.c`, `core-cpu-cache.c`, config checks, and x86 stressors; gated by architecture, compiler, and `HAVE_ASM_X86_*` macros.

Risks and test signals: inline asm constraints, PIC `%ebx` preservation, illegal instruction hazards, and infinite wait on faulty RNG flags are key risks. Signals are x86 32/64 builds, CPUID feature tests, config LAHF check, and cache flush stressors.
