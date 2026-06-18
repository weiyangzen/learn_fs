<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zicbop/prefetch.i.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zicbop/prefetch.i.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zicbop/prefetch.i.yaml` is a RISC-V ifuzz instruction descriptor for `prefetch.i` in the `Zicbop` extension family. It declares a `instruction` with assembly form `imm(xs1)` and extension gating `Zicbop`. A prefetch.i instruction indicates to hardware that the cache block whose effective address is the sum of the base address specified in xs1 and the sign-extended offset encoded in imm[11:0], where imm[4:0] equals 0b00000, is likely to be accessed by an instruction fetch in the near future.

## Important APIs, Types, and Functions

This YAML is consumed as data by the syzkaller `ifuzz` RISC-V generator rather than exporting callable code. The important schema fields are `$schema`, `kind`, `name`, `long_name`, `description`, `definedBy`, `assembly`, `format` or `encoding`, `access`, `data_independent_timing`, `pseudoinstructions`, `operation()`, and optional `sail()`. For this file, the instruction name is `prefetch.i`, long name is `Cache block prefetch for instruction fetch`, access is `s=always, u=always, vs=always, vu=always`, data-independent timing is `false`, and pseudoinstruction metadata is none.

## Control Flow

Generation control flow starts when the ifuzz tooling loads this descriptor under `gen/inst`, validates it against `inst_schema.json`, evaluates `definedBy` for the selected ISA profile, and maps `imm(xs1)` operands to either inherited format fields or explicit encoding variables. Encoding information is match pattern `-------00000-----110000000010011` with variables imm@31-25, xs1@19-15. Variable bindings are imm@31-25, xs1@19-15. The semantic lane then attaches the `operation()` block (present) and `sail()` block (absent) to generated execution or reference-model material. A prefetch.i instruction indicates to hardware that the cache block whose effective address is the sum of the base address specified in xs1 and the sign-extended offset encoded in imm[11:0], where imm[4:0] equals 0b00000, is likely to be accessed by an instruction fetch in the near future; hint-only cache prefetch behavior with immediate address offsets. The operation body updates an integer register.

## State and Persistence Behavior

The descriptor itself is static repository data and has no runtime persistence. When generated into an executor or model, its architectural state surface is: integer register file updates, microarchitectural hint or cache/fetch ordering state. Any persistent behavior comes from generated tables or compiled artifacts that embed this YAML content, not from the YAML file at runtime.

## Dependencies and Integration Points

Dependencies are inst_schema.json; explicit encoding-match parser; extension availability expression `Zicbop`. Integration points are the RISC-V instruction YAML loader, schema validator, assembler/disassembler table generation, random instruction selection in syzkaller ifuzz, semantic model generation from `operation()`/`sail()`, and extension-profile filtering for `Zicbop`. The source path and mirrored research path are significant because the research cron reconciler splits grouped reports by exact source path.

## Risks and Edge Cases

data-independent timing is explicitly false or not guaranteed; bit-field locations and immediate transforms must remain synchronized with the ISA encoding; address alignment, translation, exception ordering, and memory side effects are easy regression points.

## Test Signals

schema validation against inst_schema.json; generator round-trip checks for assembly operands and binary encoding; semantic differential tests against the Sail snippet or ISA pseudocode; memory alignment and exception-order tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zicbop/prefetch.i.yaml -->
