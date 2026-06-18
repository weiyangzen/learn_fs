<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zicond/czero.eqz.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zicond/czero.eqz.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zicond/czero.eqz.yaml` is a RISC-V ifuzz instruction descriptor for `czero.eqz` in the `Zicond` extension family. It declares a `instruction` with assembly form `xd, xs1, xs2` and extension gating `Zicond`. If xs2 contains the value zero, this instruction writes the value zero to xd. Otherwise, this instruction copies the contents of xs1 to xd. This instruction carries a syntactic dependency from both xs1 and xs2 to xd. Furthermore, if the Zkt extension is implemented, this instruction's timing is independent of the data values in xs1 and xs2.

## Important APIs, Types, and Functions

This YAML is consumed as data by the syzkaller `ifuzz` RISC-V generator rather than exporting callable code. The important schema fields are `$schema`, `kind`, `name`, `long_name`, `description`, `definedBy`, `assembly`, `format` or `encoding`, `access`, `data_independent_timing`, `pseudoinstructions`, `operation()`, and optional `sail()`. For this file, the instruction name is `czero.eqz`, long name is `Conditional zero, if condition is equal to zero`, access is `s=always, u=always, vs=always, vu=always`, data-independent timing is `false`, and pseudoinstruction metadata is none.

## Control Flow

Generation control flow starts when the ifuzz tooling loads this descriptor under `gen/inst`, validates it against `inst_schema.json`, evaluates `definedBy` for the selected ISA profile, and maps `xd, xs1, xs2` operands to either inherited format fields or explicit encoding variables. Encoding information is match pattern `0000111----------101-----0110011` with variables xs2@24-20, xs1@19-15, xd@11-7. Variable bindings are xs2@24-20, xs1@19-15, xd@11-7. The semantic lane then attaches the `operation()` block (present) and `sail()` block (present) to generated execution or reference-model material. If xs2 contains the value zero, this instruction writes the value zero to xd. Otherwise, this instruction copies the contents of xs1 to xd. This instruction carries a syntactic dependency from both xs1 and xs2 to xd. Furthermore, if the Zkt extension is implemented, this instruction's timing is independent of the data values in xs1 and xs2. The operation body updates an integer register.

## State and Persistence Behavior

The descriptor itself is static repository data and has no runtime persistence. When generated into an executor or model, its architectural state surface is: integer register file updates. Any persistent behavior comes from generated tables or compiled artifacts that embed this YAML content, not from the YAML file at runtime.

## Dependencies and Integration Points

Dependencies are inst_schema.json; explicit encoding-match parser; extension availability expression `Zicond`; RISCV Sail model snippet. Integration points are the RISC-V instruction YAML loader, schema validator, assembler/disassembler table generation, random instruction selection in syzkaller ifuzz, semantic model generation from `operation()`/`sail()`, and extension-profile filtering for `Zicond`. The source path and mirrored research path are significant because the research cron reconciler splits grouped reports by exact source path.

## Risks and Edge Cases

data-independent timing is explicitly false or not guaranteed; bit-field locations and immediate transforms must remain synchronized with the ISA encoding.

## Test Signals

schema validation against inst_schema.json; generator round-trip checks for assembly operands and binary encoding; semantic differential tests against the Sail snippet or ISA pseudocode.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zicond/czero.eqz.yaml -->
