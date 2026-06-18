<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zicsr/csrrci.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zicsr/csrrci.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zicsr/csrrci.yaml` is a RISC-V ifuzz instruction descriptor for `csrrci` in the `Zicsr` extension family. It declares a `instruction` with assembly form `xd, csr, imm` and extension gating `Zicsr`. The CSRRCI variant is similar to CSRRC, except this updates the CSR using an XLEN-bit value obtained by zero-extending a 5-bit unsigned immediate (imm[4:0]) field encoded in the `xs1` field instead of a value from an integer register. For CSRRCI, if the `imm[4:0]` field is zero, then this instruction will not write to the CSR, and shall not cause any of the side effects that might otherwise occur on a CSR write, nor raise illegal-instruction exceptions on accesses to read-only CSRs. The CSRRCI will always read the CSR and cause any read side effects regardless of `xd` and `xs1` fields.

## Important APIs, Types, and Functions

This YAML is consumed as data by the syzkaller `ifuzz` RISC-V generator rather than exporting callable code. The important schema fields are `$schema`, `kind`, `name`, `long_name`, `description`, `definedBy`, `assembly`, `format` or `encoding`, `access`, `data_independent_timing`, `pseudoinstructions`, `operation()`, and optional `sail()`. For this file, the instruction name is `csrrci`, long name is `Atomic Read and Clear Bits in CSR with Immediate`, access is `s=always, u=always, vs=always, vu=always`, data-independent timing is `false`, and pseudoinstruction metadata is when `xd == 0` to `csrci csr,imm`.

## Control Flow

Generation control flow starts when the ifuzz tooling loads this descriptor under `gen/inst`, validates it against `inst_schema.json`, evaluates `definedBy` for the selected ISA profile, and maps `xd, csr, imm` operands to either inherited format fields or explicit encoding variables. Encoding information is match pattern `-----------------111-----1110011` with variables csr@31-20, imm@19-15, xd@11-7. Variable bindings are csr@31-20, imm@19-15, xd@11-7. The semantic lane then attaches the `operation()` block (present) and `sail()` block (absent) to generated execution or reference-model material. The CSRRCI variant is similar to CSRRC, except this updates the CSR using an XLEN-bit value obtained by zero-extending a 5-bit unsigned immediate (imm[4:0]) field encoded in the `xs1` field instead of a value from an integer register. For CSRRCI, if the `imm[4:0]` field is zero, then this instruction will not write to the CSR, and shall not cause any of the side effects that might otherwise occur on a CSR write, nor raise illegal-instruction exceptions on accesses to read-only CSRs. The CSRRCI will always read the CSR and cause any read side effects regardless of `xd` and `xs1` fields; CSR read-modify-write ordering, immediate versus register operand rules, and side effects. The operation body updates an integer register, can raise architectural exceptions, uses floating-point rounding-mode control, has illegal-instruction gating.

## State and Persistence Behavior

The descriptor itself is static repository data and has no runtime persistence. When generated into an executor or model, its architectural state surface is: integer register file updates, architectural exception state. Any persistent behavior comes from generated tables or compiled artifacts that embed this YAML content, not from the YAML file at runtime.

## Dependencies and Integration Points

Dependencies are inst_schema.json; explicit encoding-match parser; extension availability expression `Zicsr`. Integration points are the RISC-V instruction YAML loader, schema validator, assembler/disassembler table generation, random instruction selection in syzkaller ifuzz, semantic model generation from `operation()`/`sail()`, and extension-profile filtering for `Zicsr`. The source path and mirrored research path are significant because the research cron reconciler splits grouped reports by exact source path.

## Risks and Edge Cases

data-independent timing is explicitly false or not guaranteed; bit-field locations and immediate transforms must remain synchronized with the ISA encoding; rounding-mode handling and illegal dynamic rounding values need coverage.

## Test Signals

schema validation against inst_schema.json; generator round-trip checks for assembly operands and binary encoding; semantic differential tests against the Sail snippet or ISA pseudocode; pseudoinstruction expansion tests; rounding-mode edge cases and NaN/exception flag tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zicsr/csrrci.yaml -->
