# File Research: sources/os/plan9/9front/sys/src/cmd/qc/gc.h

Shared header for the Power C compiler backend. It defines target sizes, object operand/program structures, register-allocation graph structures, global backend state, and cross-file function prototypes.

Key contents:
- Target data model: 32-bit `char/short/int/long/pointer`, 64-bit `vlong/double`.
- `Adr`, `Prog`, `Case`, `C1`, `Multab`, `Hintab`, `Var`, `Reg`, and `Rgn`.
- Backend globals for instruction list, switch cases, register allocation, string emission, rathole temporaries, and liveness bitsets.
- Power register policy: `REGRET`, `REGARG`, `REGMIN..REGMAX`, `REGEXT`, `REGTMP`, floating return/constants/register-variable ranges.
- Prototypes for `sgen.c`, `cgen.c`, `txt.c`, `swt.c`, `list.c`, `reg.c`, `peep.c`, and `com64.c`.

Dependencies and coupling:
- Includes the common C compiler header `../cc/cc.h` and Power object definitions `q.out.h`.
- Defines macros used by register allocation (`LOAD`, `STORE`, `BLOAD`, `BSTORE`) and register-variable bit mappings.

Filesystem/OS relevance:
- Toolchain support header; no direct filesystem behavior, but central to compiling Plan 9 Power binaries.
