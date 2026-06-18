# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsetivli.yaml

## Purpose

`vsetivli` is a RISC-V vector instruction definition for Set the vtype and vl CSRs, and write the
new value of vl into rd. It is encoded as an ifuzz instruction schema entry with assembly operands
`xd, uimm, vtypei`.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsetivli` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `xd, uimm, vtypei`.

The decoder key is `encoding.match: 11---------------111-----1010111` with variables `vtypei@29-20`,
`uimm@19-15`, `xd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

Important model helper dependencies include `get_lmul_pow`, `get_sew_pow`, `get_vlen_pow`.

## Control Flow

Execution decodes the requested `vtype` from either immediates or a source register, validates
SEW/LMUL support, computes `VLMAX`, chooses `vl` from AVL strip-mining rules, writes `vtype` and
`vl`, optionally writes `rd`, clears `vstart`, and retires. Illegal or unsupported settings set
`vill` and zero `vl` instead of producing lane operations.

## State and Persistence Behavior

This instruction mutates architectural vector CSRs: `vtype`, `vl`, and `vstart`, and writes the
selected integer destination register. It does not persist filesystem state. Its result changes the
shape and masking behavior of subsequent vector instructions.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet, vector
CSR and strip-mining helper state. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include AVL/VLMAX corner cases, reserved `vtype` bits, and `rd=x0`/`rs1=x0`
keep-vl behavior are easy to model incorrectly.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, reserved vtype
encodings, AVL values 0, VLMAX, VLMAX+1, and at least 2*VLMAX, rd/xs1 zero-register combinations.
