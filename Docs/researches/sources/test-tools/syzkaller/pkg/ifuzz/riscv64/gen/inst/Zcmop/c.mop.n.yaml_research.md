<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zcmop/c.mop.n.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zcmop/c.mop.n.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zcmop/c.mop.n.yaml` is a RISC-V ifuzz instruction descriptor for `c.mop.n` in the `Zcmop` extension family. It declares a `instruction` with assembly form `not declared` and extension gating `Zcmop`. C.MOP.n is encoded in the reserved encoding space corresponding to C.LUI xn, 0. Unlike the MOPs defined in the Zimop extension, the C.MOP.n instructions are defined to not write any register. Their encoding allows future extensions to define them to read register x[n].

## Important APIs, Types, and Functions

This YAML is consumed as data by the syzkaller `ifuzz` RISC-V generator rather than exporting callable code. The important schema fields are `$schema`, `kind`, `name`, `long_name`, `description`, `definedBy`, `assembly`, `format` or `encoding`, `access`, `data_independent_timing`, `pseudoinstructions`, `operation()`, and optional `sail()`. For this file, the instruction name is `c.mop.n`, long name is `Compressed May-Be-Operation`, access is `s=always, u=always, vs=always, vu=always`, data-independent timing is `false`, and pseudoinstruction metadata is when `(n == 0)` to `c.mop.1`; when `(n == 1)` to `c.mop.3`; when `(n == 2)` to `c.mop.5`; when `(n == 3)` to `c.mop.7`; when `(n == 4)` to `c.mop.9`; when `(n == 5)` to `c.mop.11`; when `(n == 6)` to `c.mop.13`; when `(n == 7)` to `c.mop.15`.

## Control Flow

Generation control flow starts when the ifuzz tooling loads this descriptor under `gen/inst`, validates it against `inst_schema.json`, evaluates `definedBy` for the selected ISA profile, and maps `not declared` operands to either inherited format fields or explicit encoding variables. Encoding information is match pattern `01100---10000001` with variables n@10-8. Variable bindings are n@10-8. The semantic lane then attaches the `operation()` block (empty) and `sail()` block (absent) to generated execution or reference-model material. C.MOP.n is encoded in the reserved encoding space corresponding to C.LUI xn, 0. Unlike the MOPs defined in the Zimop extension, the C.MOP.n instructions are defined to not write any register. Their encoding allows future extensions to define them to read register x[n]. The operation block is empty, so this descriptor currently contributes metadata and encoding more than executable pseudocode.

## State and Persistence Behavior

The descriptor itself is static repository data and has no runtime persistence. When generated into an executor or model, its architectural state surface is: microarchitectural hint or cache/fetch ordering state. Any persistent behavior comes from generated tables or compiled artifacts that embed this YAML content, not from the YAML file at runtime.

## Dependencies and Integration Points

Dependencies are inst_schema.json; explicit encoding-match parser; extension availability expression `Zcmop`. Integration points are the RISC-V instruction YAML loader, schema validator, assembler/disassembler table generation, random instruction selection in syzkaller ifuzz, semantic model generation from `operation()`/`sail()`, and extension-profile filtering for `Zcmop`. The source path and mirrored research path are significant because the research cron reconciler splits grouped reports by exact source path.

## Risks and Edge Cases

empty semantic body can leave downstream simulators or documentation generators without executable behavior; data-independent timing is explicitly false or not guaranteed; bit-field locations and immediate transforms must remain synchronized with the ISA encoding; compressed encodings have narrow operand sets and reserved encodings that should not be fuzzed as legal instructions.

## Test Signals

schema validation against inst_schema.json; generator round-trip checks for assembly operands and binary encoding; pseudoinstruction expansion tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zcmop/c.mop.n.yaml -->
