# File Research: sources/os/plan9/plan9/sys/src/9/rb/faultmips.c

MIPS page-fault decoding, validation, diagnostics, and alignment checking.

Key responsibilities:
- `tstbadvaddr` inspects the faulting instruction and checks whether CP0 BadVAddr matches the effective address implied by load/store opcode and base register.
- Tracks repeated identical faults to detect stuck fault handling.
- `faultsprint` optionally reports max repeated fault info.
- `faultmips` aligns fault address to page, determines read/write, calls common `fault()`, posts user notes on failure, and panics for kernel faults.
- Implements MIPS `validalign`.

Important behavior:
- Handles branch-delay faults by testing the delay-slot instruction.
- Treats TLB modification/store exceptions as writes, most others as reads.
- Ignores apparent spurious BadVAddr mismatches after logging.

Dependencies:
- Depends on `reg()` from FP/MIPS support, `seg`, `fault`, `postnote`, `tlbvirt`, and trap exception names.

Notable risks:
- Instruction decoder covers many but not every possible memory-reference opcode.
- Stuck-fault diagnostics are mostly disabled unless `Debug` is changed.
