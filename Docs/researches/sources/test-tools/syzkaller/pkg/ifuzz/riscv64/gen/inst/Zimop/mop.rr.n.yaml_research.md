<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zimop/mop.rr.n.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zimop/mop.rr.n.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zimop/mop.rr.n.yaml` is a RISC-V ifuzz instruction descriptor for `mop.rr.n` in the `Zimop` extension family. It declares a `instruction` with assembly form `xd, xs1, xs2` and extension gating `Zimop`. The Zimop extension defines 8 MOP instructions named MOP.RR.n, where n is an integer between 0 and 7, inclusive. Unless redefined by another extension, these instructions simply write 0 to X[xd]. Their encoding allows future extensions to define them to read X[xs1] and X[xs2], as well as write X[xd].

## Important APIs, Types, and Functions

This YAML is consumed as data by the syzkaller `ifuzz` RISC-V generator rather than exporting callable code. The important schema fields are `$schema`, `kind`, `name`, `long_name`, `description`, `definedBy`, `assembly`, `format` or `encoding`, `access`, `data_independent_timing`, `pseudoinstructions`, `operation()`, and optional `sail()`. For this file, the instruction name is `mop.rr.n`, long name is `May-be-operation (2 source registers)`, access is `s=always, u=always, vs=always, vu=always`, data-independent timing is `false`, and pseudoinstruction metadata is when `n == 0` to `mop.rr.0`; when `n == 1` to `mop.rr.1`; when `n == 2` to `mop.rr.2`; when `n == 3` to `mop.rr.3`; when `n == 4` to `mop.rr.4`; when `n == 5` to `mop.rr.5`; when `n == 6` to `mop.rr.6`; when `n == 7` to `mop.rr.7`.

## Control Flow

Generation control flow starts when the ifuzz tooling loads this descriptor under `gen/inst`, validates it against `inst_schema.json`, evaluates `definedBy` for the selected ISA profile, and maps `xd, xs1, xs2` operands to either inherited format fields or explicit encoding variables. Encoding information is match pattern `1-00--1----------100-----1110011` with variables n@30|27-26, xs2@24-20, xs1@19-15, xd@11-7. Variable bindings are n@30|27-26, xs2@24-20, xs1@19-15, xd@11-7. The semantic lane then attaches the `operation()` block (present) and `sail()` block (absent) to generated execution or reference-model material. The Zimop extension defines 8 MOP instructions named MOP.RR.n, where n is an integer between 0 and 7, inclusive. Unless redefined by another extension, these instructions simply write 0 to X[xd]. Their encoding allows future extensions to define them to read X[xs1] and X[xs2], as well as write X[xd]. The operation body updates an integer register.

## State and Persistence Behavior

The descriptor itself is static repository data and has no runtime persistence. When generated into an executor or model, its architectural state surface is: integer register file updates, microarchitectural hint or cache/fetch ordering state. Any persistent behavior comes from generated tables or compiled artifacts that embed this YAML content, not from the YAML file at runtime.

## Dependencies and Integration Points

Dependencies are inst_schema.json; explicit encoding-match parser; extension availability expression `Zimop`. Integration points are the RISC-V instruction YAML loader, schema validator, assembler/disassembler table generation, random instruction selection in syzkaller ifuzz, semantic model generation from `operation()`/`sail()`, and extension-profile filtering for `Zimop`. The source path and mirrored research path are significant because the research cron reconciler splits grouped reports by exact source path.

## Risks and Edge Cases

data-independent timing is explicitly false or not guaranteed; bit-field locations and immediate transforms must remain synchronized with the ISA encoding.

## Test Signals

schema validation against inst_schema.json; generator round-trip checks for assembly operands and binary encoding; semantic differential tests against the Sail snippet or ISA pseudocode; pseudoinstruction expansion tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zimop/mop.rr.n.yaml -->
