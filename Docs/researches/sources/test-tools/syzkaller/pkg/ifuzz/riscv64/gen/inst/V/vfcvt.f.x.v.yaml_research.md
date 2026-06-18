# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfcvt.f.x.v.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfcvt.f.x.v.yaml` is a riscv-unified-db YAML descriptor for the `vfcvt.f.x.v` instruction, a floating-point/integer conversion instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the unary vector form. The descriptor is `instruction` kind data, is 123 lines / 4920 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfcvt.f.x.v`, `definedBy.extension.name: V`, `assembly: vd, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `010010------00011001-----1010111` gives opcode `0x48019057`, mask `0xfc0ff07f`, and 11 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: float-to-unsigned-integer conversion, float-to-signed-integer conversion, integer/float widening or narrowing conversion to float, mask read, vector register read, vector register write, floating-point flag accrual. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs float-to-unsigned-integer conversion, float-to-signed-integer conversion, integer/float widening or narrowing conversion to float, mask read, vector register read, vector register write, floating-point flag accrual, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table. The Sail body accrues floating-point exception flags, which is a semantic test concern but is intentionally outside the ifuzz encoding table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfcvt.f.x.v` in `generated/insns.go`; the generated record has opcode `0x48019057`, mask `0xfc0ff07f`, and fields `vm`, `vs2`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
