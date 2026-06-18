<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zfh/fcvt.s.h.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zfh/fcvt.s.h.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zfh/fcvt.s.h.yaml` is a RISC-V ifuzz instruction descriptor for `fcvt.s.h` in the `Zfh` extension family. It declares a `instruction` with assembly form `fd, fs1, rm` and extension gating `Zfhmin, Zhinxmin`. Converts a single-precision number in floating-point register _fs1_ into a half-precision floating-point number in floating-point register _fd_. `fcvt.s.h` will never round, and so the 'rm' field is effectively ignored.

## Important APIs, Types, and Functions

This YAML is consumed as data by the syzkaller `ifuzz` RISC-V generator rather than exporting callable code. The important schema fields are `$schema`, `kind`, `name`, `long_name`, `description`, `definedBy`, `assembly`, `format` or `encoding`, `access`, `data_independent_timing`, `pseudoinstructions`, `operation()`, and optional `sail()`. For this file, the instruction name is `fcvt.s.h`, long name is `Convert single-precision float to a half-precision float`, access is `s=always, u=always, vs=always, vu=always`, data-independent timing is `not specified`, and pseudoinstruction metadata is none.

## Control Flow

Generation control flow starts when the ifuzz tooling loads this descriptor under `gen/inst`, validates it against `inst_schema.json`, evaluates `definedBy` for the selected ISA profile, and maps `fd, fs1, rm` operands to either inherited format fields or explicit encoding variables. Encoding information is match pattern `010000000010-------------1010011` with variables fs1@19-15, rm@14-12, fd@11-7. Variable bindings are fs1@19-15, rm@14-12, fd@11-7. The semantic lane then attaches the `operation()` block (present) and `sail()` block (present) to generated execution or reference-model material. Converts a single-precision number in floating-point register _fs1_ into a half-precision floating-point number in floating-point register _fd_. `fcvt.s.h` will never round, and so the 'rm' field is effectively ignored; vector lane behavior, masking, element width, and tail policy. The operation body is present but compact.

## State and Persistence Behavior

The descriptor itself is static repository data and has no runtime persistence. When generated into an executor or model, its architectural state surface is: no repository-local persistent state; effects are whatever downstream generators infer from the descriptor. Any persistent behavior comes from generated tables or compiled artifacts that embed this YAML content, not from the YAML file at runtime.

## Dependencies and Integration Points

Dependencies are inst_schema.json; explicit encoding-match parser; extension availability expression `Zfhmin, Zhinxmin`; RISCV Sail model snippet. Integration points are the RISC-V instruction YAML loader, schema validator, assembler/disassembler table generation, random instruction selection in syzkaller ifuzz, semantic model generation from `operation()`/`sail()`, and extension-profile filtering for `Zfhmin, Zhinxmin`. The source path and mirrored research path are significant because the research cron reconciler splits grouped reports by exact source path.

## Risks and Edge Cases

bit-field locations and immediate transforms must remain synchronized with the ISA encoding; rounding-mode handling and illegal dynamic rounding values need coverage.

## Test Signals

schema validation against inst_schema.json; generator round-trip checks for assembly operands and binary encoding; semantic differential tests against the Sail snippet or ISA pseudocode; rounding-mode edge cases and NaN/exception flag tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zfh/fcvt.s.h.yaml -->
