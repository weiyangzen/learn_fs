# File Research: sources/os/plan9/9front/sys/src/9/pc/fpu.c

Implements x86 floating-point unit initialization, trap handling, process FP state save/restore, and compatibility conversion between x87 and SSE-style `FPsave` layout.

Key elements:
- Defines CR4 feature bits for OS FXSAVE/FXRSTOR, unmasked SIMD exceptions, and XSAVE, though `putxcr0()` is a stub in this file.
- Imports low-level assembly helpers for SSE save/restore, x87 save/restore, and `ldmxcsr()`.
- Uses the SSE/FXSAVE-format `FPsave` structure as the common in-memory representation even on legacy x87-only systems.
- `fpx87save()` calls the raw x87 save routine, converts the x87 tag word into an FXSAVE tag byte, maps x87 state fields to FXSAVE-style fields, copies 80-bit x87 registers into 16-byte slots, and clears padding/MXCSR fields.
- `fpx87restore()` reconstructs the x87 tag word from the FXSAVE-style tag byte and register contents, maps fields back to legacy x87 save layout, and calls the raw restore routine.
- `mathnote()` translates FP status bits into a Plan 9 note such as invalid operation, division by zero, overflow, underflow, precision loss, stack overflow, or stack underflow.
- `matherror()` handles x87 coprocessor errors, clears the external interrupt latch for non-on-chip FPUs, saves FP state, marks it inactive, and posts a note.
- `simderror()` handles SIMD exceptions using MXCSR low status bits.
- `mathemu()` handles device-not-available traps for lazy FPU activation. It initializes first use, restores inactive FP state, saves note-time FP state when required, and checks pending unmasked exceptions before restore.
- `mathinit()` registers traps for coprocessor error, device-not-available, segment overrun, and SIMD error; on family 3 CPUs it also enables IRQ13.
- `fpuinit()` runs per CPU during identification, disables XSAVE, selects SSE or x87 save/restore based on CPUID `Sse|Fxsr`, updates CR4, and turns the FPU off for lazy use.
- `fpuprocsetup()` resets a process to `FPinit`, disables FPU, and frees any saved FP allocation chain.
- `fpuprocfork()` saves the parent active state if needed and copies FP state into the child.
- `fpuprocsave()` saves active FP state on context switch or frees state for moribund processes.
- `fpunotify()`, `fpunoted()`, and `notefpsave()` support Plan 9 note delivery with nested FP state copies so debuggers/handlers can inspect or modify saved FP context.

Filesystem relevance: none directly. It is core process/CPU state management, but it affects all kernel execution by implementing lazy FPU ownership and user-process FP exception delivery.
