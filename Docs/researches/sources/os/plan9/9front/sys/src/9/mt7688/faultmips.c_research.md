# File Research: sources/os/plan9/9front/sys/src/9/mt7688/faultmips.c

MT7688/MIPS fault handling glue. It classifies MIPS TLB/load/store faults, calls the common Plan 9 `fault` handler, posts user fault notes, and panics with register dumps on unhandled kernel faults.

`tstbadvaddr` decodes the instruction at EPC, including branch-delay handling, to check whether the computed effective address matches `badvaddr`. `ckfaultstuck` tracks repeated faults at the same VA/PC/PID/cause to diagnose faults that are not being fixed.

`validalign` enforces user pointer alignment, relaxing 64-bit alignment to 32-bit alignment for a 32-bit OS.

Notable risks: detailed fault debugging is gated by `Debug`; instruction decoding is partial and conservative.
