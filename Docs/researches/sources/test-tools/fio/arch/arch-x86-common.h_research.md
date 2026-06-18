# `sources/test-tools/fio/arch/arch-x86-common.h`

Purpose: Shared x86/x86_64 CPU feature detection for fio.

Important APIs: Defines `cpuid()` wrapper around arch-specific `do_cpuid()`, declares `ARCH_HAVE_INIT`, external `tsc_reliable` and `arch_random`, and implements `arch_init_intel()`, `arch_init_amd()`, and `arch_init()`. Intel-like vendors check TSC presence, invariant TSC via `0x80000007`, and RDRAND via CPUID leaf 1 ECX bit 30. AMD/Hygon check invariant TSC if extended leaf is available.

Control flow and integration: Included by `arch-x86.h` and `arch-x86_64.h` after they define `do_cpuid()`. Generic startup calls `arch_init()` to populate timing/random capability flags.

State and persistence: Sets process-global `tsc_reliable` and `arch_random`.

Dependencies: x86 CPUID instruction and vendor string conventions. Uses `<string.h>`.

Risks and test signals: Vendor string checks are explicit and may miss newer compatible vendors. RDRAND flag is only set in Intel-like path, not AMD. Tests should mock or run on Intel, AMD, Hygon, and virtualized CPUs to validate TSC reliability and random capability flags.
