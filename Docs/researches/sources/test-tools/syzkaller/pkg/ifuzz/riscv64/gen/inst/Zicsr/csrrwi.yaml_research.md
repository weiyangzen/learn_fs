<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zicsr/csrrwi.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zicsr/csrrwi.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zicsr/csrrwi.yaml` is a RISC-V ifuzz instruction descriptor for `csrrwi` in the `Zicsr` extension family. It declares a `instruction` with assembly form `xd, csr, imm` and extension gating `Zicsr`. Atomically write CSR using a 5-bit immediate, and load the previous value into 'xd'. Read the old value of the CSR, zero-extends the value to `XLEN` bits, and then write it to integer register xd. The 5-bit uimm field is zero-extended and written to the CSR. If `xd=x0`, then the instruction shall not read the CSR and shall not cause any of the side effects that might occur on a CSR read.

## Important APIs, Types, and Functions

This YAML is consumed as data by the syzkaller `ifuzz` RISC-V generator rather than exporting callable code. The important schema fields are `$schema`, `kind`, `name`, `long_name`, `description`, `definedBy`, `assembly`, `format` or `encoding`, `access`, `data_independent_timing`, `pseudoinstructions`, `operation()`, and optional `sail()`. For this file, the instruction name is `csrrwi`, long name is `Atomic Read/Write CSR Immediate`, access is `s=always, u=always, vs=always, vu=always`, data-independent timing is `not specified`, and pseudoinstruction metadata is when `xd == 0` to `csrwi csr,imm`.

## Control Flow

Generation control flow starts when the ifuzz tooling loads this descriptor under `gen/inst`, validates it against `inst_schema.json`, evaluates `definedBy` for the selected ISA profile, and maps `xd, csr, imm` operands to either inherited format fields or explicit encoding variables. Encoding information is match pattern `-----------------101-----1110011` with variables csr@31-20, imm@19-15, xd@11-7. Variable bindings are csr@31-20, imm@19-15, xd@11-7. The semantic lane then attaches the `operation()` block (present) and `sail()` block (present) to generated execution or reference-model material. Atomically write CSR using a 5-bit immediate, and load the previous value into 'xd'. Read the old value of the CSR, zero-extends the value to `XLEN` bits, and then write it to integer register xd. The 5-bit uimm field is zero-extended and written to the CSR. If `xd=x0`, then the instruction shall not read the CSR and shall not cause any of the side effects that might occur on a CSR read; CSR read-modify-write ordering, immediate versus register operand rules, and side effects. The operation body updates an integer register, can raise architectural exceptions, uses floating-point rounding-mode control, has illegal-instruction gating.

## State and Persistence Behavior

The descriptor itself is static repository data and has no runtime persistence. When generated into an executor or model, its architectural state surface is: integer register file updates, architectural exception state. Any persistent behavior comes from generated tables or compiled artifacts that embed this YAML content, not from the YAML file at runtime.

## Dependencies and Integration Points

Dependencies are inst_schema.json; explicit encoding-match parser; extension availability expression `Zicsr`; RISCV Sail model snippet. Integration points are the RISC-V instruction YAML loader, schema validator, assembler/disassembler table generation, random instruction selection in syzkaller ifuzz, semantic model generation from `operation()`/`sail()`, and extension-profile filtering for `Zicsr`. The source path and mirrored research path are significant because the research cron reconciler splits grouped reports by exact source path.

## Risks and Edge Cases

bit-field locations and immediate transforms must remain synchronized with the ISA encoding; rounding-mode handling and illegal dynamic rounding values need coverage.

## Test Signals

schema validation against inst_schema.json; generator round-trip checks for assembly operands and binary encoding; semantic differential tests against the Sail snippet or ISA pseudocode; pseudoinstruction expansion tests; rounding-mode edge cases and NaN/exception flag tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zicsr/csrrwi.yaml -->
