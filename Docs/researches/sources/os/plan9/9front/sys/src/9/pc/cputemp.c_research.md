# File Research: sources/os/plan9/9front/sys/src/9/pc/cputemp.c

CPU temperature `#P/cputemp` provider for Intel and AMD processors.

Key responsibilities:
- Detects Intel digital thermal sensor support through CPUID leaf 6 and reads thermal MSR `0x19c`.
- Estimates Intel TjMax, including older model handling through MSR `0xee`.
- Reads AMD temperature sensors through PCI configuration or system management network registers for supported families.
- Wires the current process to each CPU to read per-processor Intel sensor values.
- Adds `#P/cputemp` when a supported sensor path is found.

Important behavior:
- Outputs text lines in `temperature±resolution` format, with optional Intel alarm text.
- Unsupported Intel reads return `-1±-1 unsupported`.
- AMD family handling covers families `0x0f`, `0x10`-`0x16`, `0x17`, `0x19`, and `0x1a`.

Dependencies:
- Depends on CPUID/MSR helpers, PCI config access, process CPU wiring, and `addarchfile`.

Notable risks:
- AMD sensor access is noted as largely undocumented and motherboard-dependent.
- Static device lists and TjMax heuristics may be inaccurate on unrecognized CPUs.
