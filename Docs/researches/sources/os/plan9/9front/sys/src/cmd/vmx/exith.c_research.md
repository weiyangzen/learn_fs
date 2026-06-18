# File Research: sources/os/plan9/9front/sys/src/cmd/vmx/exith.c

This file handles VM exits and selected trapped x86 instructions/events.

Key behavior:
- Parses exit messages into `ExitInfo`, updates reported PC/SP/AX metadata, and dispatches by exit name.
- Handles port I/O exits, including string I/O with segment/address-size handling and `x86access`.
- Handles EPT faults by attempting single-step emulation through `x86step`.
- Initializes and filters CPUID leaves, exposes a KVM-like hypervisor leaf, masks unsupported features, and sizes XSAVE state based on `xcr0`.
- Handles RDMSR/WRMSR for PAT, microcode update, and `IA32_MISC_ENABLE`; unknown MSRs are debug-logged.
- Handles debug/control-register moves, debug exceptions, HLT, IRQ ack notifications, and XSETBV validation.
- Unknown instruction exits inject `#ud`; unknown fatal exits either mark VM dead or call `sysfatal` depending on `persist`.

Integration and risks:
- CPUID masking is a guest compatibility contract; changing it can break OS boot.
- String I/O must correctly update RCX/RSI/RDI on partial fault.
