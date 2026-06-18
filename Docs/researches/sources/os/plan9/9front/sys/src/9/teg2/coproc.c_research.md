# File Research: sources/os/plan9/9front/sys/src/9/teg2/coproc.c

Runtime coprocessor access helpers for ARM. Because ARM encodes coprocessor/register fields directly in instructions, this file builds two-instruction stubs in memory, flushes data cache, invalidates I-cache, and calls them to read/write CP15 and VFP control/register state.

`cprd`/`cpwr` generate MRC/MCR operations; `cprdsc`/`cpwrsc` specialize CP15. `fprd`/`fpwr` generate VMRS/VMSR for FP control registers. `fpsavereg`/`fprestreg` generate VSTR/VLDR for double FP registers.

All operations run at `splhi` and use cache maintenance to make generated instructions executable and coherent.
