<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zkne/aes32esi.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zkne/aes32esi.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zkne/aes32esi.yaml` is a RISC-V ifuzz instruction descriptor for `aes32esi` in the `Zkne` extension family. It declares a `instruction` with assembly form `xd, xs1, xs2, bs` and extension gating `Zkne`. No prose description is supplied in the YAML.

## Important APIs, Types, and Functions

This YAML is consumed as data by the syzkaller `ifuzz` RISC-V generator rather than exporting callable code. The important schema fields are `$schema`, `kind`, `name`, `long_name`, `description`, `definedBy`, `assembly`, `format` or `encoding`, `access`, `data_independent_timing`, `pseudoinstructions`, `operation()`, and optional `sail()`. For this file, the instruction name is `aes32esi`, long name is `No synopsis available`, access is `s=always, u=always, vs=always, vu=always`, data-independent timing is `true`, and pseudoinstruction metadata is none.

## Control Flow

Generation control flow starts when the ifuzz tooling loads this descriptor under `gen/inst`, validates it against `inst_schema.json`, evaluates `definedBy` for the selected ISA profile, and maps `xd, xs1, xs2, bs` operands to either inherited format fields or explicit encoding variables. Encoding information is match pattern `--10001----------000-----0110011` with variables bs@31-30, xs2@24-20, xs1@19-15, xd@11-7. Variable bindings are bs@31-30, xs2@24-20, xs1@19-15, xd@11-7. The semantic lane then attaches the `operation()` block (empty) and `sail()` block (absent) to generated execution or reference-model material. AES round/key-schedule transformation details. The operation block is empty, so this descriptor currently contributes metadata and encoding more than executable pseudocode.

## State and Persistence Behavior

The descriptor itself is static repository data and has no runtime persistence. When generated into an executor or model, its architectural state surface is: no repository-local persistent state; effects are whatever downstream generators infer from the descriptor. Any persistent behavior comes from generated tables or compiled artifacts that embed this YAML content, not from the YAML file at runtime.

## Dependencies and Integration Points

Dependencies are inst_schema.json; explicit encoding-match parser; extension availability expression `Zkne`. Integration points are the RISC-V instruction YAML loader, schema validator, assembler/disassembler table generation, random instruction selection in syzkaller ifuzz, semantic model generation from `operation()`/`sail()`, and extension-profile filtering for `Zkne`. The source path and mirrored research path are significant because the research cron reconciler splits grouped reports by exact source path.

## Risks and Edge Cases

empty semantic body can leave downstream simulators or documentation generators without executable behavior; constant-time metadata should stay aligned with the real data path; bit-field locations and immediate transforms must remain synchronized with the ISA encoding; cryptographic helper semantics require bit-exact known-answer tests.

## Test Signals

schema validation against inst_schema.json; generator round-trip checks for assembly operands and binary encoding; cryptographic known-answer vectors.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zkne/aes32esi.yaml -->
