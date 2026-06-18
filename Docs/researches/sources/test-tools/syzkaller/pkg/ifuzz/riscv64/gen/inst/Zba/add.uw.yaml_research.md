<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zba/add.uw.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zba/add.uw.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zba/add.uw.yaml` is a RISC-V ifuzz instruction descriptor for `add.uw` in the `Zba` extension family. It declares a `instruction` with assembly form `xd, xs1, xs2` and extension gating `Zba`. Performs an XLEN-wide addition between xs2 and the zero-extended least-significant word of xs1.

## Important APIs, Types, and Functions

This YAML is consumed as data by the syzkaller `ifuzz` RISC-V generator rather than exporting callable code. The important schema fields are `$schema`, `kind`, `name`, `long_name`, `description`, `definedBy`, `assembly`, `format` or `encoding`, `access`, `data_independent_timing`, `pseudoinstructions`, `operation()`, and optional `sail()`. For this file, the instruction name is `add.uw`, long name is `Add unsigned word`, access is `s=always, u=always, vs=always, vu=always`, data-independent timing is `not specified`, and pseudoinstruction metadata is when `xs2 == 0` to `zext.w xd, xs1`.

## Control Flow

Generation control flow starts when the ifuzz tooling loads this descriptor under `gen/inst`, validates it against `inst_schema.json`, evaluates `definedBy` for the selected ISA profile, and maps `xd, xs1, xs2` operands to either inherited format fields or explicit encoding variables. Encoding information is inherits inst_subtype/R/R-x.yaml#/data; opcodes funct7=4, funct3=ADD.UW, opcode=inst_opcode/OP-32.yaml#/data. Variable bindings are no explicit variable list beyond inherited format/assembly operands. The semantic lane then attaches the `operation()` block (present) and `sail()` block (present) to generated execution or reference-model material. Performs an XLEN-wide addition between xs2 and the zero-extended least-significant word of xs1. The operation body updates an integer register, consults or updates CSR state, can raise architectural exceptions, has illegal-instruction gating.

## State and Persistence Behavior

The descriptor itself is static repository data and has no runtime persistence. When generated into an executor or model, its architectural state surface is: integer register file updates, CSR reads or writes, architectural exception state. Any persistent behavior comes from generated tables or compiled artifacts that embed this YAML content, not from the YAML file at runtime.

## Dependencies and Integration Points

Dependencies are inst_schema.json; shared `inst_subtype`/`inst_opcode` YAML fragments; extension availability expression `Zba`; RISCV Sail model snippet. Integration points are the RISC-V instruction YAML loader, schema validator, assembler/disassembler table generation, random instruction selection in syzkaller ifuzz, semantic model generation from `operation()`/`sail()`, and extension-profile filtering for `Zba`. The source path and mirrored research path are significant because the research cron reconciler splits grouped reports by exact source path.

## Risks and Edge Cases

schema drift can silently change generated assembler/disassembler behavior.

## Test Signals

schema validation against inst_schema.json; generator round-trip checks for assembly operands and binary encoding; semantic differential tests against the Sail snippet or ISA pseudocode; pseudoinstruction expansion tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zba/add.uw.yaml -->
