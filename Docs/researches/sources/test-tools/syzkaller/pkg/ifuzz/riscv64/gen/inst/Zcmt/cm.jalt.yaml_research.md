<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zcmt/cm.jalt.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zcmt/cm.jalt.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zcmt/cm.jalt.yaml` is a RISC-V ifuzz instruction descriptor for `cm.jalt` in the `Zcmt` extension family. It declares a `instruction` with assembly form `index` and extension gating `Zcmt`. Read an address from the Jump Vector Table and jump to it, linking to `ra`.

## Important APIs, Types, and Functions

This YAML is consumed as data by the syzkaller `ifuzz` RISC-V generator rather than exporting callable code. The important schema fields are `$schema`, `kind`, `name`, `long_name`, `description`, `definedBy`, `assembly`, `format` or `encoding`, `access`, `data_independent_timing`, `pseudoinstructions`, `operation()`, and optional `sail()`. For this file, the instruction name is `cm.jalt`, long name is `Jump Via Table with Optional Link`, access is `s=always, u=always, vs=always, vu=always`, data-independent timing is `not specified`, and pseudoinstruction metadata is none.

## Control Flow

Generation control flow starts when the ifuzz tooling loads this descriptor under `gen/inst`, validates it against `inst_schema.json`, evaluates `definedBy` for the selected ISA profile, and maps `index` operands to either inherited format fields or explicit encoding variables. Encoding information is match pattern `101000--------10` with variables index@9-2. Variable bindings are index@9-2 (not=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]). The semantic lane then attaches the `operation()` block (present) and `sail()` block (absent) to generated execution or reference-model material. Read an address from the Jump Vector Table and jump to it, linking to `ra`; jump-table dispatch through control-transfer table state. The operation body updates an integer register, consults or updates CSR state, can raise architectural exceptions, has illegal-instruction gating.

## State and Persistence Behavior

The descriptor itself is static repository data and has no runtime persistence. When generated into an executor or model, its architectural state surface is: integer register file updates, CSR reads or writes, architectural exception state. Any persistent behavior comes from generated tables or compiled artifacts that embed this YAML content, not from the YAML file at runtime.

## Dependencies and Integration Points

Dependencies are inst_schema.json; explicit encoding-match parser; extension availability expression `Zcmt`. Integration points are the RISC-V instruction YAML loader, schema validator, assembler/disassembler table generation, random instruction selection in syzkaller ifuzz, semantic model generation from `operation()`/`sail()`, and extension-profile filtering for `Zcmt`. The source path and mirrored research path are significant because the research cron reconciler splits grouped reports by exact source path.

## Risks and Edge Cases

bit-field locations and immediate transforms must remain synchronized with the ISA encoding; compressed encodings have narrow operand sets and reserved encodings that should not be fuzzed as legal instructions.

## Test Signals

schema validation against inst_schema.json; generator round-trip checks for assembly operands and binary encoding; semantic differential tests against the Sail snippet or ISA pseudocode.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zcmt/cm.jalt.yaml -->
