<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/x86/decode.go -->
# sources/test-tools/syzkaller/pkg/ifuzz/x86/decode.go

## Purpose
`decode.go` implements the x86 ifuzz instruction-length decoder and optional external XED decoder hook. It aims to avoid failing on correct instructions, while accepting that it can falsely decode some incorrect byte sequences.

## Important APIs, Types, And Functions
The main method is `func (insnset *InsnSet) Decode(mode iset.Mode, text []byte) (int, error)`. It also defines package variable `XedDecode func(mode iset.Mode, text []byte) (int, error)`, prefix maps `prefixes32` and `prefixes64`, and `func (insnset *InsnSet) DecodeExt(mode, text)` for XED integration.

## Control Flow
`Decode` rejects zero-length input, initializes operand/immediate/displacement/address sizes by mode, detects VEX/XOP prefixes with special LDS/LES/POP exclusions, or consumes legacy prefixes while adjusting sizes for `0x66`, `0x67`, and REX.W. It then scans `insnset.Insns`, filtering by mode, VEX presence/map, prefix restrictions, opcode bytes, optional short-register opcode (`Srm`), ModRM constraints, SIB/displacement length, immediate lengths, and suffix bytes. On the first match it returns the decoded byte length; otherwise it returns `unknown instruction`.

## State and Persistence Behavior
There is no disk persistence. Runtime state is the global `XedDecode` hook and static prefix maps. Decode does not mutate instruction descriptors; it only consumes the registered `InsnSet`.

## Dependencies and Integration Points
The file depends on `fmt` and `pkg/ifuzz/iset`. It integrates with generated x86 descriptors, x86 `Insn` metadata, the generic ifuzz decoder interface, and optional XED-backed differential/external decoding through `DecodeExt`.

## Risks and Test Signals
The function is intentionally heuristic and complex. Risks include decode-order ambiguity, prefix handling mistakes, VEX/XOP false positives, ModRM/SIB displacement length bugs, mode-size mistakes, and accepting invalid instruction streams. `DecodeExt` returns a sentinel success length of zero when XED is enabled but no text is provided, which callers must interpret carefully. Tests should cover prefix-only errors, truncated VEX/ModRM/SIB/immediate paths, REX/operand-size interactions, XED hook behavior, and known byte sequences across 16/32/64-bit modes.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/x86/decode.go -->
