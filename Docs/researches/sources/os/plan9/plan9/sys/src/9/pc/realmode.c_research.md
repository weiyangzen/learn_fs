# File Research: sources/os/plan9/plan9/sys/src/9/pc/realmode.c

Kernel bridge for executing BIOS calls by temporarily returning the processor to real mode.

Key elements:
- `realmode` locks global real-mode access, copies input `Ureg` to the low real-mode register block, copies low assembly code, identity-maps low memory, disables interrupts/PIC/APIC, calls `realmode0`, restores mappings/CR3/interrupts, and returns registers.
- Obeys `*norealmode`.
- `rtrapread`/`rtrapwrite` expose a `realmode` arch file for controlled VBE INT 10h calls.
- `rmemread`/`rmemwrite` expose `realmodemem`, allowing reads below 1MB and writes only to the real-mode buffer page or VGA framebuffer range.
- `realmodelink` registers both arch files.

Interactions:
- `memory.c` uses `realmode` for E820 BIOS calls.
- VGA/APM paths may also use real-mode BIOS services.

Research notes:
- Not VM86; it fully disables hardware interrupts during BIOS execution.
- Security/robustness is managed by narrow arch-file validation.
