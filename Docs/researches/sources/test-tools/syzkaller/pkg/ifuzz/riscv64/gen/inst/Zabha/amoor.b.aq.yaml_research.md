# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoor.b.aq.yaml

Source facts: `amoor.b.aq` / `Atomic fetch-and-or byte (acquire)`; 143 lines; width `8`; ordering `acquire`; match `0100010----------000-----0101111`.

## Purpose
Defines `amoor.b.aq`, a Zabha narrow atomic bitwise OR instruction for a 8-bit byte memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `0100010----------000-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amoor.b.aq`, declares extension `Zabha`, and maps the operation to the shared AMO helper as `amo<8>(virtual_address, X[xs2][7:0], AmoOperation::Or, aq=1, rl=0, $encoding)`. The operation block checks the base atomic extension through `ExtensionName::A` and optional `CSR[misa].A`, then applies the ordering hooks required by the suffix.
For the current ifuzz generator, this source contributes one generated instruction template named `amoor.b.aq`. The 32-bit match string yields opcode-family bits `0100010`, aq/rl encoding bits `10` (acquire), funct3 `000` (byte), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject if the A extension gate fails; for `acquire` ordering, calls `memory_model_acquire()` before the atomic helper; load the address from `X[xs1]`; call `amo<8>` with the low 8 bits of `xs2`; store the helper return value in `X[xd]`. The embedded Sail reference expands that helper into effective-address validation, address translation, write-effective-address announcement, read, `bitwise OR` result calculation, write-back of the narrow result, sign-extended return of the original loaded value into `rd`, and memory-exception handling.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main semantic risk is extension-gate drift: the file is under `Zabha` and `definedBy.extension.name` is `Zabha`, but both the operation block and Sail block use the base A-extension gate. That may be inherited from the wider Zaamo templates; for byte/halfword AMOs it should be checked against the intended Zabha availability rules. Ifuzz generation itself ignores this semantic block, so the risk affects semantic consumers more than the current opcode table.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded byte, and correct aq/rl propagation with aq set and rl clear.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amoor.b.aq` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `0100010----------000-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=1, rl=0 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `A` and calculates `bitwise OR` through the AMO operation match. For this instruction, ORs the narrow xs2 operand with the loaded byte/halfword and writes the narrow result.
