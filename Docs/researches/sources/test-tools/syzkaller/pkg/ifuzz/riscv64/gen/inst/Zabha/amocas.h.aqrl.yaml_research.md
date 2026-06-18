# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amocas.h.aqrl.yaml

Source facts: `amocas.h.aqrl` / `Atomic compare-and-swap halfword (acquire-release)`; 137 lines; width `16`; ordering `acquire-release`; match `0010111----------001-----0101111`.

## Purpose
Defines `amocas.h.aqrl`, a Zabha narrow atomic compare-and-swap instruction for a 16-bit halfword memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `0010111----------001-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amocas.h.aqrl`, binds it to extension `Zabha`, and describes a CAS operation over `X[xs1]`. The executable pseudocode currently checks `implemented?(ExtensionName::Zabha)`, derives `virtual_address = X[xs1]`, and leaves the real helper call commented as `amocas16(..., X[xs2][15:0], X[xd][15:0], aq=1, rl=1, $encoding)`.
For the current ifuzz generator, this source contributes one generated instruction template named `amocas.h.aqrl`. The 32-bit match string yields opcode-family bits `0010111`, aq/rl encoding bits `11` (acquire-release), funct3 `001` (halfword), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject when Zabha is not implemented; for `acquire-release` ordering, calls `memory_model_acquire()` before the atomic helper and `memory_model_release()` after it; obtain the memory address from `xs1`; then the intended CAS helper would compare the loaded halfword with the low 16 bits of `xs2`, write the replacement value from `xd` on success, and return the loaded value in `xd` sign-extended. The embedded Sail block is more complete: it resolves and translates the data address, announces the write effective address, reads the memory value, compares it to `rs2_val`, conditionally writes `rd_val`, writes the loaded value back to `X(rd)`, and routes memory exceptions through the Sail exception handlers.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main risk is semantic incompleteness: `operation()` still contains `# TODO` and the helper call is commented, so any consumer that executes the operation DSL would not model the CAS side effect. A second risk is wording drift: the description mentions writing `xs2+1`, while the commented operation and Sail block use `xd`/`rd` as the replacement source. That mismatch should be resolved against the authoritative ISA source before relying on these comments for test generation.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded halfword, and correct aq/rl propagation with aq set and rl set.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amocas.h.aqrl` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `0010111----------001-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=1, rl=1 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `Zabha`, not the base A gate, which matches the source directory and `definedBy` extension. It uses `mem_read`/`mem_write_value` with aq=1 and rl=1 semantics encoded through the memory calls.
