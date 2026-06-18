# sources/test-tools/stress-ng/stress-easy-opcode.c

Purpose: implements `easy-opcode`, a CPU stressor that generates executable pages filled with random simple architecture-specific opcodes plus a return instruction, then repeatedly executes the buffer in a child process.

Important APIs/types/functions: `stress_easy_opcode_t` describes byte sequences. `easy_opcodes[]` is selected by architecture/endian macros and `HAVE_MPROTECT`. `stress_easy_opcode_fill()` writes random easy opcodes into a buffer and appends `stress_ret_opcode`. `stress_easy_opcode_state_t` stores shared bogo count and opcode count. `stress_easy_opcode()` manages mmap, mprotect, fork, execution loop, and metric.

Control flow: after verifying return-opcode support, the stressor maps shared state and private opcode pages with guard pages. It forks a child each cycle; the child protects guard pages, writes opcodes into the executable region, switches it to `PROT_READ | PROT_EXEC`, flushes I-cache, then calls the buffer repeatedly until stop or max ops. The parent waits and copies child bogo count to stress-ng. Final metric is easy opcodes executed per second.

State and persistence behavior: all state is anonymous mmap; no files are created. The child updates shared `state->bogo_ops` and `state->ops`. On x86 it emits `cld` after buffer execution to restore direction flag because some allowed opcodes manipulate flags.

Dependencies and integration points: uses architecture macros, `core-asm-ret`, mmap/mprotect, fork/killpid/scheduler helpers, and stress-ng metrics. Unsupported architectures or missing `mprotect()` register unimplemented.

Risks: generated machine code is inherently architecture-sensitive. The opcode table must only contain safe non-privileged instructions and must preserve control flow to the appended return. W^X, SELinux, or hardened kernels may reject executable anonymous mappings. Child isolation prevents a bad opcode from directly corrupting parent state.

Test signals: build on supported architectures, run short timeouts, verify nonzero opcode-rate metric, and ensure unsupported architectures report unimplemented rather than failing at runtime.
