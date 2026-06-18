<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zfa/fround.s.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zfa/fround.s.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zfa/fround.s.yaml` is a RISC-V ifuzz instruction descriptor for `fround.s` in the `Zfa` extension family. It declares a `instruction` with assembly form `fd, fs1, rm` and extension gating `Zfa`. Rounds the single-precision floating-point number in floating-point register _fs1_ to an integer, according to the rounding mode specified in the instruction’s _rm_ field. It then writes that integer, represented as a single-precision floating-point number, to floating-point register _fd_. Zero and infinite inputs are copied to _fd_ unmodified. Signaling NaN inputs cause the invalid operation exception flag to be set; no other exception flags are set. FROUND.S is encoded like FCVT.S.D, but with rs2=4.

## Important APIs, Types, and Functions

This YAML is consumed as data by the syzkaller `ifuzz` RISC-V generator rather than exporting callable code. The important schema fields are `$schema`, `kind`, `name`, `long_name`, `description`, `definedBy`, `assembly`, `format` or `encoding`, `access`, `data_independent_timing`, `pseudoinstructions`, `operation()`, and optional `sail()`. For this file, the instruction name is `fround.s`, long name is `Floating-point round single-precision float to integer`, access is `s=always, u=always, vs=always, vu=always`, data-independent timing is `true`, and pseudoinstruction metadata is none.

## Control Flow

Generation control flow starts when the ifuzz tooling loads this descriptor under `gen/inst`, validates it against `inst_schema.json`, evaluates `definedBy` for the selected ISA profile, and maps `fd, fs1, rm` operands to either inherited format fields or explicit encoding variables. Encoding information is match pattern `010000000100-------------1010011` with variables fs1@19-15, rm@14-12, fd@11-7. Variable bindings are fs1@19-15, rm@14-12, fd@11-7. The semantic lane then attaches the `operation()` block (present) and `sail()` block (present) to generated execution or reference-model material. Rounds the single-precision floating-point number in floating-point register _fs1_ to an integer, according to the rounding mode specified in the instruction’s _rm_ field. It then writes that integer, represented as a single-precision floating-point number, to floating-point register _fd_. Zero and infinite inputs are copied to _fd_ unmodified. Signaling NaN inputs cause the invalid operation exception flag to be set; no other exception flags are set. FROUND.S is encoded like FCVT.S.D, but with rs2=4. The operation body uses single-precision floating-point semantics, uses floating-point rounding-mode control.

## State and Persistence Behavior

The descriptor itself is static repository data and has no runtime persistence. When generated into an executor or model, its architectural state surface is: no repository-local persistent state; effects are whatever downstream generators infer from the descriptor. Any persistent behavior comes from generated tables or compiled artifacts that embed this YAML content, not from the YAML file at runtime.

## Dependencies and Integration Points

Dependencies are inst_schema.json; explicit encoding-match parser; extension availability expression `Zfa`; RISCV Sail model snippet. Integration points are the RISC-V instruction YAML loader, schema validator, assembler/disassembler table generation, random instruction selection in syzkaller ifuzz, semantic model generation from `operation()`/`sail()`, and extension-profile filtering for `Zfa`. The source path and mirrored research path are significant because the research cron reconciler splits grouped reports by exact source path.

## Risks and Edge Cases

constant-time metadata should stay aligned with the real data path; bit-field locations and immediate transforms must remain synchronized with the ISA encoding; rounding-mode handling and illegal dynamic rounding values need coverage.

## Test Signals

schema validation against inst_schema.json; generator round-trip checks for assembly operands and binary encoding; semantic differential tests against the Sail snippet or ISA pseudocode; rounding-mode edge cases and NaN/exception flag tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zfa/fround.s.yaml -->
