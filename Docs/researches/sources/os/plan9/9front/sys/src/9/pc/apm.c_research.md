# File Research: sources/os/plan9/9front/sys/src/9/pc/apm.c

Advanced Power Management 1.2 BIOS bridge for 32-bit PC kernels.

Key responsibilities:
- Parses APM register values passed from boot configuration through `isaconfig("apm", ...)`.
- Builds the required consecutive GDT descriptors for APM 32-bit code, 16-bit code, and data segments.
- Exposes `#P/apm`, where reads return the saved `Ureg` argument/result block and writes perform an APM BIOS far call.
- Resets the i8253 timer after APM set-power-state calls because some BIOSes disable timers during suspend.

Important behavior:
- Forces the APM code segment lengths to `0xffffffff` as a workaround for bad BIOS-reported 16-bit lengths.
- Uses `apmfarcall(APMCSEL, ebx, &apmu)` at high interrupt priority.
- Converts real-mode-style segment bases by shifting APM segment values left by four before installing descriptors.

Dependencies:
- Depends on `apmjump.s`, x86 GDT layout, `ISAConf`, `addarchfile`, `i8253reset`, and segment constants from `mem.h`.

Notable risks:
- The file intentionally knows GDT bit layout and uses `KADDR(base)` before descriptor encoding.
- The `#P/apm` write interface requires an exact `Ureg`-sized payload and is privileged by file mode only.
