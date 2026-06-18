# File Research: sources/os/plan9/9front/sys/src/cmd/9c/txt.c

This file is the main Power64 text/instruction emission layer for `9c`. It initializes backend state, manages registers and calling convention temporaries, maps compiler IR operations to Power64 assembly opcodes, and defines type widths/cast compatibility.

Key routines:
- `ginit` initializes target identity (`thechar='9'`, `thestring="power64"`), register reservations, standard constant/register nodes, pseudo symbols, and 64-bit helper state.
- `gclean` checks leaked registers, flushes pending string data, emits `AGLOBL` declarations, appends `AEND`, and calls `outcode`.
- `nextpc`, `gins`, `gopcode`, `gbranch`, `patch`, and `gpseudo` build the `Prog` stream.
- `gargs` and `garg1` evaluate and place call arguments, including struct-by-pointer and first-register-argument handling.
- `regalloc`, `regfree`, `regsalloc`, `regaalloc`, and `regaalloc1` implement simple backend register and stack argument allocation.
- `naddr` and `raddr` translate compiler `Node` values into assembler `Adr` operands.
- `gmove` emits type-aware moves and conversions, including integer/float conversions, memory loads/stores, immediate zero handling, and common floating constants.
- `sval`, `sconst`, `uconst`, and `exreg` classify immediate/register possibilities.
- `ewidth` and `ncast` define target type sizes and legal cast categories.

Important interactions:
- Produces Power64 `Prog` records consumed by `swt.c` object serialization and later by `9l`.
- Relies on reserved registers such as `REGZERO`, `REGTMP`, `REGSP`, `REGRET`, `FREGRET`, `FREGCVI`, and floating constants.
- Uses `typechlpv`, `typefd`, `typeu`, and `typesu` tables from the shared compiler frontend.

Research notes:
- Integer-to-float conversion is implemented with the classic `0x43300000` double-bias trick and includes unsigned adjustment for `TULONG`.
- Floating constants like 0, 0.5, 1, and 2 use pre-reserved floating registers.
- The backend treats `TVLONG`, `TUVLONG`, and `TIND` as 64-bit integer-like values via the `isv` macro.
