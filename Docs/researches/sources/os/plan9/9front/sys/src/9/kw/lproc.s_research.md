# File Research: sources/os/plan9/9front/sys/src/9/kw/lproc.s

Small Kirkwood ARM process-transition assembly file. `touser` creates the first transition to user mode by installing the user stack pointer, setting SPSR to user mode, pushing the user entry PC (`UTZERO+0x20`), and returning through the simulated `RFE`.

`forkret` restores a saved trap frame for a newly forked process and returns to the interrupted context through `RFE`.

Notable risks: comments document that Plan 9 assembler `RFE` is not the ARMv6 instruction but a pre-v6 load-multiple-with-SPSR behavior; this is tightly coupled to trap-frame layout.
