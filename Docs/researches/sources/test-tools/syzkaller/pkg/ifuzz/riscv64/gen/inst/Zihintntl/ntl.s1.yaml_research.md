<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zihintntl/ntl.s1.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zihintntl/ntl.s1.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zihintntl/ntl.s1.yaml` is a RISC-V ifuzz instruction descriptor for `ntl.s1` in the `Zihintntl` extension family. It declares a `instruction` with assembly form `not declared` and extension gating `Zihintntl`. The NTL.S1 instruction indicates that the immediately subsequent instruction does not exhibit temporal locality within the capacity of the innermost level of shared cache in the memory hierarchy. NTL.S1 is encoded as ADD x0, x0, x4.

## Important APIs, Types, and Functions

This YAML is consumed as data by the syzkaller `ifuzz` RISC-V generator rather than exporting callable code. The important schema fields are `$schema`, `kind`, `name`, `long_name`, `description`, `definedBy`, `assembly`, `format` or `encoding`, `access`, `data_independent_timing`, `pseudoinstructions`, `operation()`, and optional `sail()`. For this file, the instruction name is `ntl.s1`, long name is `Non-temporal locality hint, innermost shared`, access is `s=always, u=always, vs=always, vu=always`, data-independent timing is `false`, and pseudoinstruction metadata is none.

## Control Flow

Generation control flow starts when the ifuzz tooling loads this descriptor under `gen/inst`, validates it against `inst_schema.json`, evaluates `definedBy` for the selected ISA profile, and maps `not declared` operands to either inherited format fields or explicit encoding variables. Encoding information is match pattern `00000000010000000000000000110011`. Variable bindings are no explicit variable list beyond inherited format/assembly operands. The semantic lane then attaches the `operation()` block (empty) and `sail()` block (absent) to generated execution or reference-model material. The NTL.S1 instruction indicates that the immediately subsequent instruction does not exhibit temporal locality within the capacity of the innermost level of shared cache in the memory hierarchy. NTL.S1 is encoded as ADD x0, x0, x4. The operation block is empty, so this descriptor currently contributes metadata and encoding more than executable pseudocode.

## State and Persistence Behavior

The descriptor itself is static repository data and has no runtime persistence. When generated into an executor or model, its architectural state surface is: microarchitectural hint or cache/fetch ordering state. Any persistent behavior comes from generated tables or compiled artifacts that embed this YAML content, not from the YAML file at runtime.

## Dependencies and Integration Points

Dependencies are inst_schema.json; explicit encoding-match parser; extension availability expression `Zihintntl`. Integration points are the RISC-V instruction YAML loader, schema validator, assembler/disassembler table generation, random instruction selection in syzkaller ifuzz, semantic model generation from `operation()`/`sail()`, and extension-profile filtering for `Zihintntl`. The source path and mirrored research path are significant because the research cron reconciler splits grouped reports by exact source path.

## Risks and Edge Cases

empty semantic body can leave downstream simulators or documentation generators without executable behavior; data-independent timing is explicitly false or not guaranteed.

## Test Signals

schema validation against inst_schema.json; generator round-trip checks for assembly operands and binary encoding.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zihintntl/ntl.s1.yaml -->
