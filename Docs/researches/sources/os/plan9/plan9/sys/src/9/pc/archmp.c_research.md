# File Research: sources/os/plan9/plan9/sys/src/9/pc/archmp.c

PC multiprocessor architecture selection and TSC-based clock support.

Key responsibilities:
- Defines `archmp`, a `PCArch` implementation for Intel MP Specification systems.
- `identify()` respects `*nomp`, searches for `_MP_`, validates the MP floating pointer and `PCMP` table checksum/version, and selects MP mode or uniprocessor fallback.
- Uses LAPIC/IOAPIC interrupt functions for MP systems.
- Uses `i8253read` or `tscticks` as fast clock depending on CPU server/TSC availability.
- `mpresetothers()` sends INIT to all CPUs except self.
- `syncclock()` synchronizes TSC values across processors.
- `tscticks()` reads the TSC and reports CPU Hz.

Important behavior:
- Does not accept default MP configurations with physical address 0.
- Prints a uniprocessor assumption message when no MP table is found.

Dependencies:
- Depends on MP structures, `sigsearch`, LAPIC/MP interrupt initialization, i8253, TSC/MSR helpers, and global `arch`.

Notable risks:
- ACPI is acknowledged but not used for interrupt routing here.
- TSC sync assumes CPU0 ticks progress and that writing MSR 0x10 is valid.
