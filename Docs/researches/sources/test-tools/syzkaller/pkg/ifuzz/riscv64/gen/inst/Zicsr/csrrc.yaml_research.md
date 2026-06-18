<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zicsr/csrrc.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zicsr/csrrc.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zicsr/csrrc.yaml` is a RISC-V ifuzz instruction descriptor for `csrrc` in the `Zicsr` extension family. It declares a `instruction` with assembly form `xd, csr, xs1` and extension gating `Zicsr`. The CSRRC (Atomic Read and Clear Bits in CSR) instruction reads the value of the CSR, zero-extends the value to XLEN bits, and writes it to integer register `xd`. The initial value in integer register `xs1` is treated as a bit mask that specifies bit positions to be cleared in the CSR. Any bit that is high in `xs1` will cause the corresponding bit to be cleared in the CSR, if that CSR bit is writable. For CSRRC, if `xs1=x0`, then the instruction will not write to the CSR at all, and so shall not cause any of the side effects that might otherwise occur on a CSR write, nor raise illegal- instruction exceptions on accesses to read-only CSRs. CSRRC always reads the addressed CSR and cause any read side effects regardless of `xs1` and `xd` fields. Note that if `xs1` specifies a register other than `x0`, and that register holds a zero value, the instruction will not action any attendant per-field side effects, but will action any side effects caused by writing to the entire CSR.

## Important APIs, Types, and Functions

This YAML is consumed as data by the syzkaller `ifuzz` RISC-V generator rather than exporting callable code. The important schema fields are `$schema`, `kind`, `name`, `long_name`, `description`, `definedBy`, `assembly`, `format` or `encoding`, `access`, `data_independent_timing`, `pseudoinstructions`, `operation()`, and optional `sail()`. For this file, the instruction name is `csrrc`, long name is `Atomic Read and Clear Bits in CSR`, access is `s=always, u=always, vs=always, vu=always`, data-independent timing is `false`, and pseudoinstruction metadata is when `xd == 0` to `csrc csr,xs1`.

## Control Flow

Generation control flow starts when the ifuzz tooling loads this descriptor under `gen/inst`, validates it against `inst_schema.json`, evaluates `definedBy` for the selected ISA profile, and maps `xd, csr, xs1` operands to either inherited format fields or explicit encoding variables. Encoding information is match pattern `-----------------011-----1110011` with variables csr@31-20, xs1@19-15, xd@11-7. Variable bindings are csr@31-20, xs1@19-15, xd@11-7. The semantic lane then attaches the `operation()` block (present) and `sail()` block (absent) to generated execution or reference-model material. The CSRRC (Atomic Read and Clear Bits in CSR) instruction reads the value of the CSR, zero-extends the value to XLEN bits, and writes it to integer register `xd`. The initial value in integer register `xs1` is treated as a bit mask that specifies bit positions to be cleared in the CSR. Any bit that is high in `xs1` will cause the corresponding bit to be cleared in the CSR, if that CSR bit is writable. For CSRRC, if `xs1=x0`, then the instruction will not write to the CSR at all, and so shall not cause any of the side effects that might otherwise occur on a CSR write, nor raise illegal- instruction exceptions on accesses to read-only CSRs. CSRRC always reads the addressed CSR and cause any read side effects regardless of `xs1` and `xd` fields. Note that if `xs1` specifies a register other than `x0`, and that register holds a zero value, the instruction will not action any attendant per-field side effects, but will action any side effects caused by writing to the entire CSR; CSR read-modify-write ordering, immediate versus register operand rules, and side effects. The operation body updates an integer register, can raise architectural exceptions, uses floating-point rounding-mode control, has illegal-instruction gating.

## State and Persistence Behavior

The descriptor itself is static repository data and has no runtime persistence. When generated into an executor or model, its architectural state surface is: integer register file updates, architectural exception state. Any persistent behavior comes from generated tables or compiled artifacts that embed this YAML content, not from the YAML file at runtime.

## Dependencies and Integration Points

Dependencies are inst_schema.json; explicit encoding-match parser; extension availability expression `Zicsr`. Integration points are the RISC-V instruction YAML loader, schema validator, assembler/disassembler table generation, random instruction selection in syzkaller ifuzz, semantic model generation from `operation()`/`sail()`, and extension-profile filtering for `Zicsr`. The source path and mirrored research path are significant because the research cron reconciler splits grouped reports by exact source path.

## Risks and Edge Cases

data-independent timing is explicitly false or not guaranteed; bit-field locations and immediate transforms must remain synchronized with the ISA encoding; rounding-mode handling and illegal dynamic rounding values need coverage.

## Test Signals

schema validation against inst_schema.json; generator round-trip checks for assembly operands and binary encoding; semantic differential tests against the Sail snippet or ISA pseudocode; pseudoinstruction expansion tests; rounding-mode edge cases and NaN/exception flag tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zicsr/csrrc.yaml -->
