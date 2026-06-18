<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zbkb/brev8.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zbkb/brev8.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zbkb/brev8.yaml` is a RISC-V ifuzz instruction descriptor for `brev8` in the `Zbkb` extension family. It declares a `instruction` with assembly form `xd, xs1` and extension gating `Zbkb`. Reverses the order of the bits in every byte of a register.

## Important APIs, Types, and Functions

This YAML is consumed as data by the syzkaller `ifuzz` RISC-V generator rather than exporting callable code. The important schema fields are `$schema`, `kind`, `name`, `long_name`, `description`, `definedBy`, `assembly`, `format` or `encoding`, `access`, `data_independent_timing`, `pseudoinstructions`, `operation()`, and optional `sail()`. For this file, the instruction name is `brev8`, long name is `Reverse bits in bytes`, access is `s=always, u=always, vs=always, vu=always`, data-independent timing is `false`, and pseudoinstruction metadata is none.

## Control Flow

Generation control flow starts when the ifuzz tooling loads this descriptor under `gen/inst`, validates it against `inst_schema.json`, evaluates `definedBy` for the selected ISA profile, and maps `xd, xs1` operands to either inherited format fields or explicit encoding variables. Encoding information is match pattern `011010000111-----101-----0010011` with variables xs1@19-15, xd@11-7. Variable bindings are xs1@19-15, xd@11-7. The semantic lane then attaches the `operation()` block (present) and `sail()` block (present) to generated execution or reference-model material. Reverses the order of the bits in every byte of a register; vector lane behavior, masking, element width, and tail policy. The operation body updates an integer register.

## State and Persistence Behavior

The descriptor itself is static repository data and has no runtime persistence. When generated into an executor or model, its architectural state surface is: integer register file updates. Any persistent behavior comes from generated tables or compiled artifacts that embed this YAML content, not from the YAML file at runtime.

## Dependencies and Integration Points

Dependencies are inst_schema.json; explicit encoding-match parser; extension availability expression `Zbkb`; RISCV Sail model snippet. Integration points are the RISC-V instruction YAML loader, schema validator, assembler/disassembler table generation, random instruction selection in syzkaller ifuzz, semantic model generation from `operation()`/`sail()`, and extension-profile filtering for `Zbkb`. The source path and mirrored research path are significant because the research cron reconciler splits grouped reports by exact source path.

## Risks and Edge Cases

data-independent timing is explicitly false or not guaranteed; bit-field locations and immediate transforms must remain synchronized with the ISA encoding.

## Test Signals

schema validation against inst_schema.json; generator round-trip checks for assembly operands and binary encoding; semantic differential tests against the Sail snippet or ISA pseudocode.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zbkb/brev8.yaml -->
