# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfirst.m.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfirst.m.yaml` is a riscv-unified-db YAML descriptor for the `vfirst.m` instruction, a mask query instruction in the RISC-V `V` vector extension. It records the assembler spelling `xd, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the assembly form `xd, vs2, vm`. The descriptor is `instruction` kind data, is 67 lines / 1720 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfirst.m`, `definedBy.extension.name: V`, `assembly: xd, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `010000------10001010-----1010111` gives opcode `0x4008a057`, mask `0xfc0ff07f`, and 11 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `xd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: mask read, first active mask-bit index search. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_vd_unmasked`, `assert_vstart`, reads the mask and relevant operands (vs2), initializes an inactive-lane-preserving result, loops across active elements, performs mask read, first active mask-bit index search, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table. Sail writes `X(rd)` with the first active mask index or -1, while the generated metadata only exposes the `xd` bit field.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- The instruction writes an integer register (`xd`) rather than a vector destination; keeping the destination field name distinct is important for operand decoding.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfirst.m` in `generated/insns.go`; the generated record has opcode `0x4008a057`, mask `0xfc0ff07f`, and fields `vm`, `vs2`, `xd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
