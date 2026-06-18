# File Research: sources/os/plan9/9front/sys/src/cmd/aux/icanhasvmx.c

Role: Intel VMX capability probe and MSR decoder.

Checks:
- Runs `/bin/aux/cpuid` in a child and scans `features` lines for `vmx`.
- Opens `#P/msr` and reads VMX MSRs.
- In default mode, attempts to set feature-control bits in MSR `0x3a`, then checks secondary controls, EPT, VPID, and unrestricted guest support.

Output modes:
- Default prints whether VMX is supported and whether required features are missing.
- `-v` prints decoded VMX control capabilities, VMCS revision/size/memory type, misc fields, fixed CR0/CR4 bits, VMCS enum, EPT, and VPID features.
- `-r` prints raw MSR values and implies verbose.

Implementation:
- `printbits` marks forced bits with `!` and wraps long lines.
- Uses "true" control MSRs when VMX basic indicates extended controls.

Caveat:
- The program opens `#P/msr` with `OREAD` but default mode calls `wrmsr`; behavior depends on Plan 9 device semantics and permissions.
