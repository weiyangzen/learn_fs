<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zcmp/cm.mva01s.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zcmp/cm.mva01s.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zcmp/cm.mva01s.yaml` is a RISC-V ifuzz instruction descriptor for `cm.mva01s` in the `Zcmp` extension family. It declares a `instruction` with assembly form `r1s, r2s` and extension gating `Zcmp`. Moves r1s' into a0 and r2s' into a1. The execution is atomic, so it is not possible to observe state where only one of a0 or a1 have been updated. The encoding uses sreg number specifiers instead of xreg number specifiers to save encoding space. The mapping between them is specified in the pseudo-code below.

## Important APIs, Types, and Functions

This YAML is consumed as data by the syzkaller `ifuzz` RISC-V generator rather than exporting callable code. The important schema fields are `$schema`, `kind`, `name`, `long_name`, `description`, `definedBy`, `assembly`, `format` or `encoding`, `access`, `data_independent_timing`, `pseudoinstructions`, `operation()`, and optional `sail()`. For this file, the instruction name is `cm.mva01s`, long name is `Move two s0-s7 registers into a0-a1`, access is `s=always, u=always, vs=always, vu=always`, data-independent timing is `not specified`, and pseudoinstruction metadata is none.

## Control Flow

Generation control flow starts when the ifuzz tooling loads this descriptor under `gen/inst`, validates it against `inst_schema.json`, evaluates `definedBy` for the selected ISA profile, and maps `r1s, r2s` operands to either inherited format fields or explicit encoding variables. Encoding information is match pattern `101011---11---10` with variables r1s@9-7, r2s@4-2. Variable bindings are r1s@9-7, r2s@4-2. The semantic lane then attaches the `operation()` block (present) and `sail()` block (absent) to generated execution or reference-model material. Moves r1s' into a0 and r2s' into a1. The execution is atomic, so it is not possible to observe state where only one of a0 or a1 have been updated. The encoding uses sreg number specifiers instead of xreg number specifiers to save encoding space. The mapping between them is specified in the pseudo-code below; vector lane behavior, masking, element width, and tail policy. The operation body updates an integer register, consults or updates CSR state, can raise architectural exceptions, has illegal-instruction gating.

## State and Persistence Behavior

The descriptor itself is static repository data and has no runtime persistence. When generated into an executor or model, its architectural state surface is: integer register file updates, CSR reads or writes, architectural exception state. Any persistent behavior comes from generated tables or compiled artifacts that embed this YAML content, not from the YAML file at runtime.

## Dependencies and Integration Points

Dependencies are inst_schema.json; explicit encoding-match parser; extension availability expression `Zcmp`. Integration points are the RISC-V instruction YAML loader, schema validator, assembler/disassembler table generation, random instruction selection in syzkaller ifuzz, semantic model generation from `operation()`/`sail()`, and extension-profile filtering for `Zcmp`. The source path and mirrored research path are significant because the research cron reconciler splits grouped reports by exact source path.

## Risks and Edge Cases

bit-field locations and immediate transforms must remain synchronized with the ISA encoding; compressed encodings have narrow operand sets and reserved encodings that should not be fuzzed as legal instructions.

## Test Signals

schema validation against inst_schema.json; generator round-trip checks for assembly operands and binary encoding; semantic differential tests against the Sail snippet or ISA pseudocode.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zcmp/cm.mva01s.yaml -->
