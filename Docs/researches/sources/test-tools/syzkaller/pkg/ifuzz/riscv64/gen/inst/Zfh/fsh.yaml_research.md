<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zfh/fsh.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zfh/fsh.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zfh/fsh.yaml` is a RISC-V ifuzz instruction descriptor for `fsh` in the `Zfh` extension family. It declares a `instruction` with assembly form `fs2, imm(xs1)` and extension gating `Zfhmin`. The `fsh` instruction stores a half-precision floating-point value from register _xd_ to memory at address _xs1_ + _imm_. `fsh` does not modify the bits being transferred; in particular, the payloads of non-canonical NaNs are preserved. `fsh` ignores all but the lower 16 bits in _fs2_. `fsh` is only guaranteed to execute atomically if the effective address is naturally aligned.

## Important APIs, Types, and Functions

This YAML is consumed as data by the syzkaller `ifuzz` RISC-V generator rather than exporting callable code. The important schema fields are `$schema`, `kind`, `name`, `long_name`, `description`, `definedBy`, `assembly`, `format` or `encoding`, `access`, `data_independent_timing`, `pseudoinstructions`, `operation()`, and optional `sail()`. For this file, the instruction name is `fsh`, long name is `Half-precision floating-point store`, access is `s=always, u=always, vs=always, vu=always`, data-independent timing is `not specified`, and pseudoinstruction metadata is none.

## Control Flow

Generation control flow starts when the ifuzz tooling loads this descriptor under `gen/inst`, validates it against `inst_schema.json`, evaluates `definedBy` for the selected ISA profile, and maps `fs2, imm(xs1)` operands to either inherited format fields or explicit encoding variables. Encoding information is match pattern `-----------------001-----0100111` with variables imm@31-25|11-7, xs1@19-15, fs2@24-20. Variable bindings are imm@31-25|11-7, xs1@19-15, fs2@24-20. The semantic lane then attaches the `operation()` block (present) and `sail()` block (present) to generated execution or reference-model material. The `fsh` instruction stores a half-precision floating-point value from register _xd_ to memory at address _xs1_ + _imm_. `fsh` does not modify the bits being transferred; in particular, the payloads of non-canonical NaNs are preserved. `fsh` ignores all but the lower 16 bits in _fs2_. `fsh` is only guaranteed to execute atomically if the effective address is naturally aligned. The operation body writes architectural memory, updates an integer register.

## State and Persistence Behavior

The descriptor itself is static repository data and has no runtime persistence. When generated into an executor or model, its architectural state surface is: integer register file updates, architectural memory writes. Any persistent behavior comes from generated tables or compiled artifacts that embed this YAML content, not from the YAML file at runtime.

## Dependencies and Integration Points

Dependencies are inst_schema.json; explicit encoding-match parser; extension availability expression `Zfhmin`; RISCV Sail model snippet. Integration points are the RISC-V instruction YAML loader, schema validator, assembler/disassembler table generation, random instruction selection in syzkaller ifuzz, semantic model generation from `operation()`/`sail()`, and extension-profile filtering for `Zfhmin`. The source path and mirrored research path are significant because the research cron reconciler splits grouped reports by exact source path.

## Risks and Edge Cases

bit-field locations and immediate transforms must remain synchronized with the ISA encoding; address alignment, translation, exception ordering, and memory side effects are easy regression points.

## Test Signals

schema validation against inst_schema.json; generator round-trip checks for assembly operands and binary encoding; semantic differential tests against the Sail snippet or ISA pseudocode; memory alignment and exception-order tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zfh/fsh.yaml -->
