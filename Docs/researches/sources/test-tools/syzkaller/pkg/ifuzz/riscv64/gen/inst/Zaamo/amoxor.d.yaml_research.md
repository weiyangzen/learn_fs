<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoxor.d.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoxor.d.yaml

## Purpose

`amoxor.d.yaml` describes `amoxor.d`, atomic fetch-and-xor doubleword, for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a doubleword atomic read-modify-write instruction with unordered ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amoxor.d`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0010000----------011-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x2000302f` and opcode mask `0xfe00707f`. `definedBy` requires `Zaamo` and `xlen: 64`. The operation semantics use width `64` bits, source slice `X[xs2]`, operation `Xor`, aq bit `0`, and rl bit `0`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amoxor.d` loads the doubleword at address `X[xs1]`, writes the loaded doubleword into `xd`, then XORs the source operand with the loaded memory value and stores the low-width result. The executable `operation()` block first rejects the instruction when extension `A` is not implemented or is disabled in `misa`, then applies any acquire hook, reads `X[xs1]` as the virtual address, calls `amo<64>` with `X[xs2]`, `AmoOperation::Xor`, aq=`0`, rl=`0`, and finally applies the release hook when present. The Sail block expands the helper into address checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, exception handling, and destination-register writeback.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amoxor.d` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares `Zaamo` while the executable operation checks extension `A`, matching the base atomic extension gating used by these Zaamo AMO descriptors. Doubleword form is RV64-only, so losing the `xlen: 64` gate would let the descriptor name survive generation while target semantics are invalid on RV32. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amoxor.d` is emitted with match `0010000----------011-----0101111`, opcode `0x2000302f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amoxor.d`, include operation-specific checks for `Xor` and memory-order bits aq=`0`/rl=`0`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoxor.d.yaml -->
