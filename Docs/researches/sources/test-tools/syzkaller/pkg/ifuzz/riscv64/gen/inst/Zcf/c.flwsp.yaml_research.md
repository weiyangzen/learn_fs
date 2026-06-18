<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zcf/c.flwsp.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zcf/c.flwsp.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zcf/c.flwsp.yaml` is a RISC-V ifuzz instruction descriptor for `c.flwsp` in the `Zcf` extension family. It declares a `instruction` with assembly form `fd, imm(sp)` and extension gating `Zcf`. Loads a single-precision floating-point value from memory into floating-point register fd. It computes its effective address by adding the zero-extended offset, scaled by 4, to the stack pointer, x2. It expands to `flw` `fd, offset(x2)`.

## Important APIs, Types, and Functions

This YAML is consumed as data by the syzkaller `ifuzz` RISC-V generator rather than exporting callable code. The important schema fields are `$schema`, `kind`, `name`, `long_name`, `description`, `definedBy`, `assembly`, `format` or `encoding`, `access`, `data_independent_timing`, `pseudoinstructions`, `operation()`, and optional `sail()`. For this file, the instruction name is `c.flwsp`, long name is `Load word into floating-point register from stack`, access is `s=always, u=always, vs=always, vu=always`, data-independent timing is `not specified`, and pseudoinstruction metadata is none.

## Control Flow

Generation control flow starts when the ifuzz tooling loads this descriptor under `gen/inst`, validates it against `inst_schema.json`, evaluates `definedBy` for the selected ISA profile, and maps `fd, imm(sp)` operands to either inherited format fields or explicit encoding variables. Encoding information is match pattern `011-----------10` with variables imm@3-2|12|6-4, fd@11-7. Variable bindings are imm@3-2|12|6-4 (left_shift=2), fd@11-7. The semantic lane then attaches the `operation()` block (present) and `sail()` block (absent) to generated execution or reference-model material. Loads a single-precision floating-point value from memory into floating-point register fd. It computes its effective address by adding the zero-extended offset, scaled by 4, to the stack pointer, x2. It expands to `flw` `fd, offset(x2)`. The operation body reads architectural memory, updates an integer register, consults or updates CSR state, can raise architectural exceptions, has illegal-instruction gating.

## State and Persistence Behavior

The descriptor itself is static repository data and has no runtime persistence. When generated into an executor or model, its architectural state surface is: integer register file updates, CSR reads or writes, architectural memory reads, architectural exception state. Any persistent behavior comes from generated tables or compiled artifacts that embed this YAML content, not from the YAML file at runtime.

## Dependencies and Integration Points

Dependencies are inst_schema.json; explicit encoding-match parser; extension availability expression `Zcf`. Integration points are the RISC-V instruction YAML loader, schema validator, assembler/disassembler table generation, random instruction selection in syzkaller ifuzz, semantic model generation from `operation()`/`sail()`, and extension-profile filtering for `Zcf`. The source path and mirrored research path are significant because the research cron reconciler splits grouped reports by exact source path.

## Risks and Edge Cases

bit-field locations and immediate transforms must remain synchronized with the ISA encoding; address alignment, translation, exception ordering, and memory side effects are easy regression points; compressed encodings have narrow operand sets and reserved encodings that should not be fuzzed as legal instructions.

## Test Signals

schema validation against inst_schema.json; generator round-trip checks for assembly operands and binary encoding; semantic differential tests against the Sail snippet or ISA pseudocode; memory alignment and exception-order tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zcf/c.flwsp.yaml -->
