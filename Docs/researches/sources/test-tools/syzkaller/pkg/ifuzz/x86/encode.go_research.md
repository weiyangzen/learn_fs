<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/x86/encode.go -->
# sources/test-tools/syzkaller/pkg/ifuzz/x86/encode.go

## Purpose
`encode.go` implements random x86 instruction encoding for ifuzz descriptors. It turns an `Insn` template plus an `iset.Config` and RNG into bytes, including prefixes, opcodes, ModRM/SIB, displacement, immediates, and suffixes.

## Important APIs, Types, And Functions
The main API is `func (insn *Insn) Encode(cfg *iset.Config, r *rand.Rand) []byte`. It calls `cfg.IsCompatible`, pseudo `generator` functions, and `generateArg` for displacement/immediate bytes. It reads many `Insn` metadata fields: `Vex`, `VexMap`, `VexL`, `VexP`, `VexNoR`, `Rexw`, `Prefix`, `No66Prefix`, `NoRepPrefix`, `Mem32`, `Opcode`, `Srm`, `Modrm`, `Reg`, `Rm`, `Mod`, `NoSibDisp`, `Avx2Gather`, `Imm`, `Imm2`, and `Suffix`.

## Control Flow
The method panics if the instruction is incompatible with the requested mode, delegates pseudo instructions, initializes size defaults by mode, and then branches between legacy and VEX/XOP encodings. Legacy encoding may add random harmless prefixes, required prefixes, and optional REX; prefixes update operand/address/immediate sizes. VEX encoding constructs three-byte prefixes with randomized or constrained R/X/B/W/L/pp/vvvv fields. The encoder then appends opcode bytes, encodes `Srm` or full ModRM, optionally emits SIB and displacement bytes, appends immediate operands after translating sentinel sizes (`-1`, `-2`, `-3`), and finally appends suffix bytes.

## State and Persistence Behavior
The function has no persistent state but consumes RNG state heavily, so output is deterministic only for a fixed `rand.Rand` seed and descriptor. It does not mutate descriptors, except through local variables. Panics are used for impossible mode/compatibility errors.

## Dependencies and Integration Points
The file depends on `math/rand` and `pkg/ifuzz/iset`. It integrates with x86 descriptor generation, pseudo instruction generators, the x86 decoder, and generic ifuzz generation loops. The Intel/AMD manual comment documents the architectural basis for the encoding rules.

## Risks and Test Signals
Risks include generating prefixes that alter semantics unexpectedly, incorrect size recalculation for `0x66`/`0x67`/REX.W, VEX bit inversion mistakes, invalid AVX2 gather register combinations, and ModRM/SIB displacement edge cases. Random generation can hide rare failures without deterministic seeds. Tests should round-trip encoded bytes through `Decode`, compare selected cases with XED when available, cover all modes and sentinel immediate sizes, and include gather-specific register exclusion checks.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/x86/encode.go -->
