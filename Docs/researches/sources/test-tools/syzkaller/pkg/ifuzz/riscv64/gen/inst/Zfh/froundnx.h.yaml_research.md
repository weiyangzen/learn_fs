<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zfh/froundnx.h.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zfh/froundnx.h.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zfh/froundnx.h.yaml` is a RISC-V ifuzz instruction descriptor for `froundnx.h` in the `Zfh` extension family. It declares a `instruction` with assembly form `fd, fs1, rm` and extension gating `Zfa, Zfh`. No prose description is supplied in the YAML.

## Important APIs, Types, and Functions

This YAML is consumed as data by the syzkaller `ifuzz` RISC-V generator rather than exporting callable code. The important schema fields are `$schema`, `kind`, `name`, `long_name`, `description`, `definedBy`, `assembly`, `format` or `encoding`, `access`, `data_independent_timing`, `pseudoinstructions`, `operation()`, and optional `sail()`. For this file, the instruction name is `froundnx.h`, long name is `No synopsis available`, access is `s=always, u=always, vs=always, vu=always`, data-independent timing is `false`, and pseudoinstruction metadata is none.

## Control Flow

Generation control flow starts when the ifuzz tooling loads this descriptor under `gen/inst`, validates it against `inst_schema.json`, evaluates `definedBy` for the selected ISA profile, and maps `fd, fs1, rm` operands to either inherited format fields or explicit encoding variables. Encoding information is match pattern `010001000101-------------1010011` with variables fs1@19-15, rm@14-12, fd@11-7. Variable bindings are fs1@19-15, rm@14-12, fd@11-7. The semantic lane then attaches the `operation()` block (empty) and `sail()` block (absent) to generated execution or reference-model material. one RISC-V instruction entry used by the generator. The operation block is empty, so this descriptor currently contributes metadata and encoding more than executable pseudocode.

## State and Persistence Behavior

The descriptor itself is static repository data and has no runtime persistence. When generated into an executor or model, its architectural state surface is: no repository-local persistent state; effects are whatever downstream generators infer from the descriptor. Any persistent behavior comes from generated tables or compiled artifacts that embed this YAML content, not from the YAML file at runtime.

## Dependencies and Integration Points

Dependencies are inst_schema.json; explicit encoding-match parser; extension availability expression `Zfa, Zfh`. Integration points are the RISC-V instruction YAML loader, schema validator, assembler/disassembler table generation, random instruction selection in syzkaller ifuzz, semantic model generation from `operation()`/`sail()`, and extension-profile filtering for `Zfa, Zfh`. The source path and mirrored research path are significant because the research cron reconciler splits grouped reports by exact source path.

## Risks and Edge Cases

empty semantic body can leave downstream simulators or documentation generators without executable behavior; data-independent timing is explicitly false or not guaranteed; bit-field locations and immediate transforms must remain synchronized with the ISA encoding; rounding-mode handling and illegal dynamic rounding values need coverage.

## Test Signals

schema validation against inst_schema.json; generator round-trip checks for assembly operands and binary encoding; rounding-mode edge cases and NaN/exception flag tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zfh/froundnx.h.yaml -->
