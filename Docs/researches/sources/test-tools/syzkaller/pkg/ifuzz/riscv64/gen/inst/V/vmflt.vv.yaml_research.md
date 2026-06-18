# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmflt.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmflt.vv.yaml` is a riscv-unified-db YAML
descriptor for `vmflt.vv`, a floating-point compare-to-mask in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, vs1, vm`, access policy, a 32-bit encoding pattern, operand bit ranges,
and an optional Sail reference body. Semantically, this descriptor represents floating-point less-
than comparison producing a mask bit per active element. This is the vector-vector form; both
element operands are read from vector register groups.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 77
lines / 2239 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmflt.vv`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`011011-----------001-----1010111`, which computes to opcode `0x6c001057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow computes SEW/LMUL/VLMAX, checks FP compare legality, reads mask and
operands, initializes a mask destination preserving inactive lanes, evaluates the selected FP
predicate per active element, writes `vd` as a mask register, clears `vstart`, and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.
- Floating-point exceptions, NaN behavior, FRM legality, and illegal SEW=8 behavior are architectural semantics in Sail but not constraints in the generated instruction table.

The Sail body reads `fcsr.FRM()`, rejects illegal FP compare destinations with
`illegal_fp_vd_unmasked`, asserts `SEW != 8`, preserves inactive destination mask bits via
`init_masked_result_cmp`, and writes mask bits with `write_vmask`.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmflt.vv` is emitted.
- Check the generated entry has opcode `0x6c001057`, mask `0xfc00707f`, and fields `vm, vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include legal FP element widths, illegal SEW=8, NaNs, FP exception flags, masked inactive lanes, and destination mask alias cases.
