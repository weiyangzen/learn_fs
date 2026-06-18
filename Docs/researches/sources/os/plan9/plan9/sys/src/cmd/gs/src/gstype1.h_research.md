# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstype1.h

## Purpose
Declares the client interface and shared opcode definitions for Type 1 and Type 2 charstring interpreters.

## Public Surface
- `crypt_charstring_seed`: Type 1 charstring decryption seed.
- Opaque `gs_type1_state`, `gx_path`, `gs_font_type1`, and `gs_type1_data_s` declarations.
- Initialization/configuration APIs: `gs_type1_interp_init`, `gs_type1_set_callback_data`, `gs_type1_set_lsb`, `gs_type1_set_width`.
- Backward-compatible `gs_type1_init` macro.
- Interpreter result codes: `type1_result_sbw`, `type1_result_callothersubr`.
- `charstring_interpret_proc` and function-pointer typedef.
- Interpreter prototypes: `gs_type1_interpret`, `gs_type2_interpret`.

## Charstring Encoding Definitions
- `char_num_command` defines numeric opcode ranges for one-byte numbers, two-byte positive/negative numbers, and related value macros.
- `char_command` defines shared Type 1/Type 2 opcodes, Type 1-only commands, Type 2-only commands, and undefined-case macros for each interpreter.
- `char1_command_names` and `char2_command_names` provide debug names.
- `char1_extended_command` enumerates Type 1 escape commands such as `dotsection`, `vstem3`, `hstem3`, `seac`, `sbw`, `div`, `callothersubr`, `pop`, and `setcurrentpoint`.
- `char2_extended_command` enumerates Type 2 escape commands including logical/math/stack ops and flex variants.

## Dependencies
Uses Ghostscript glyph data, imager state, log2 scaling, path, font, fixed data, and charstring internals through surrounding includes in implementation files.

## Risks and Notes
- The header intentionally combines Type 1 and Type 2 opcode definitions because the command sets overlap heavily.
- The backward-compatible `gs_type1_init` macro appears mismatched with the newer `gs_type1_interp_init` signature in this source snapshot; active callers use the direct initializer.
