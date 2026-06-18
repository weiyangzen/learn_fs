# File Research: sources/os/plan9/9front/sys/src/cmd/5i/run.c

This file is the ARM instruction execution core for `5i`, the Plan 9/9front ARM interpreter. It defines the instruction dispatch table `itab[]`, condition-code evaluation, the main fetch/decode/execute loop, and handlers for supported ARM data processing, multiply, swap, load/store, block transfer, branch, branch-with-link, and SWI instructions.

Key elements:
- `itab[]` maps decoded `armclass()` values to handler functions, mnemonic names, and broad instruction categories used by profiling/statistics.
- `run()` fetches from emulated `REGPC`, decodes the instruction class, evaluates the stored compare/test state against the instruction condition field, dispatches the handler if true, advances `REGPC`, and checks breakpoints.
- `runcmp()`, `runteq()`, and `runtst()` implement the interpreter’s simplified condition model using `reg.cc1`, `reg.cc2`, and `reg.compare_op`.
- `shift()` implements ARM shifter operand behavior, including carry-out maintenance.
- `dpex()` implements core data-processing operations and updates comparison/carry state when `Sbit` is present.
- `Idp0` through `Idp3` cover register, shifted-register, register-shifted-register, and rotated-immediate data processing forms.
- `Imul`, `Imula`, and `Imull` implement multiply, multiply-accumulate, and long multiply variants with undefined-instruction checks for illegal register combinations.
- `Imem1` and `Imem2` implement word/byte and halfword/signed-byte memory operations via `getmem_*` and `putmem_*`.
- `Ilsm()` implements LDM/STM for non-PC register lists and rejects PC and `S`-bit cases.
- `Ib()` and `Ibl()` implement PC-relative branch and branch-with-link, with optional call-tree tracing.

Dependencies and integration:
- Relies on global interpreter state from `arm.h`: `reg`, `memory`, tracing flags, breakpoint list, and helper routines.
- Calls `Ssyscall()` for SWI dispatch, implemented in `syscall.c`.
- Uses symbol helpers `findsym()`, `printparams()`, and `printsource()` for call-tree output.

Notable behavior:
- PC reads use ARM pipeline adjustment by adding 8 in operand fetches.
- Branch handlers set `REGPC` to target minus 4 because `run()` increments PC after handler execution.
- Unsupported instructions or illegal encodings call `undef()`, print context, and `longjmp(errjmp, 0)`.
- Several ARM operations are intentionally incomplete, for example ADC/SBC/RSC in `dpex()` trap as undefined.

Research notes:
- This is not a full ARM emulator; it is a practical user-level interpreter for old Plan 9 ARM binaries.
- Memory and syscall behavior are delegated to the emulator runtime rather than modeled here.
