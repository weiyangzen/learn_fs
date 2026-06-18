# File Research: sources/os/plan9/plan9/sys/src/cmd/qc/list.c

PowerPC compiler backend listing/formatting support.

Key responsibilities:
- Installs custom Plan 9 format verbs for assembler diagnostics and debug output.
- Formats bitsets of optimization variables, instructions, opcodes, addresses, string constants, and symbol-relative names.
- Handles PowerPC address classes including integer, floating, condition-register, branch, string, and floating constants.
- Prints symbolic storage names for extern/static/auto/param references.

Dependencies:
- Uses backend globals from `gc.h`: `anames`, `var`, `pc`, `Bits`, `Prog`, `Adr`, and symbol/type conventions.
- Shared with optimizer/debug flags that print `%P`, `%D`, `%B`, `%A`, `%N`, and `%S`.

Notable risks:
- Formatting is diagnostic infrastructure, so wrong output can make backend debugging misleading.
- `Bconv` truncates long bitsets silently at `STRINGSZ`.
- `Pconv` depends on the backend’s three-address `from/from3/reg/to` encoding.
