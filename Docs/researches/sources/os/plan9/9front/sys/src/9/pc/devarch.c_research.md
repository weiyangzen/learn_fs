# File Research: sources/os/plan9/9front/sys/src/9/pc/devarch.c

PC `#P/arch` device plus CPU identification, architecture selection, low-level controls, and hardware watchpoint setup.

Key responsibilities:
- Implements `#P` files for byte/word/long I/O port access, MSR access, and dynamically registered architecture files.
- Provides `addarchfile()` for other PC subsystems such as ACPI, APM, HDA, and CPU temperature.
- Initializes I/O allocation policy and optional `ioexclude` reservations.
- Identifies CPU vendor/family/model/features, enables TSC, PSE, MCE/MCA, PGE, PAT write-combining, MTRRs, NX, RDRAND, watchpoint width, and FPU support.
- Chooses the active `PCArch` from `knownarch[]` and fills missing hooks from the generic architecture.
- Exposes `cputype`, `archctl`, and `realmodemem` arch files.
- Implements `archctl` controls for PGE, memory-barrier strategy, and MTRR cache regions.
- Provides idle behavior, ISA config parsing, machine-check dump support, NMI enable/handler, and debug watchpoint programming.

Important behavior:
- Raw I/O access checks that ports are unused, with VGA register exceptions.
- `realmodemem` reads below 1 MiB and only permits writes to VGA framebuffer range.
- Coherence defaults progress from no-op to `mb586` or `mfence` depending on CPU features.
- On 386, copy-on-reference is selected because compare-and-swap is interrupt-disabled emulation.

Dependencies:
- Depends on port I/O, MSR/CPUID/CR4 helpers, MTRR, FPU, trap/NMI, `knownarch`, device framework, and kernel configuration parsing.

Notable risks:
- `#P/iob`, `#P/iow`, `#P/iol`, and `#P/msr` are intentionally powerful debugging interfaces.
- CPU tables contain many trial-and-error or guesswork model names/delay constants.
