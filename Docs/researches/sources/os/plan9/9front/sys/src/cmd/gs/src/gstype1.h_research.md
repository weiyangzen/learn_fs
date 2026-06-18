# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gstype1.h

Declares the Type 1/Type 2 charstring interpreter interface and opcode definitions.

Key definitions:
- `crypt_charstring_seed` for Type 1 charstring decryption.
- Opaque `gs_type1_state` and Type 1 font/path forward declarations.
- Initialization and state customization APIs: `gs_type1_interp_init`, callback data setter, left sidebearing setter, and width setter.
- Return codes `type1_result_sbw` and `type1_result_callothersubr`.
- Generic `charstring_interpret_proc_t`, with declarations for `gs_type1_interpret` and `gs_type2_interpret`.
- Shared Type 1/Type 2 number encoding opcodes and helpers for small, positive two-byte, and negative two-byte values.
- `char_command` enum for shared, Type 1-only, and Type 2-only charstring commands.
- Debug name tables for Type 1 and Type 2 commands.
- `char1_extended_command` and `char2_extended_command` enums plus debug-name tables for escaped commands.

Research notes:
- The header intentionally co-locates Type 1 and Type 2 opcode definitions because the encodings overlap heavily.
- The backward-compatibility `gs_type1_init` macro adapts older text enumerator usage to the newer interpreter init function.
