<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zimop/mop.r.n.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zimop/mop.r.n.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zimop/mop.r.n.yaml` is a RISC-V ifuzz instruction descriptor for `mop.r.n` in the `Zimop` extension family. It declares a `instruction` with assembly form `xd, xs1` and extension gating `Zimop`. Unless redefined by another extension, this instructions simply writes 0 to X[xd]. The encoding allows future extensions to define them to read X[xs1], as well as write X[xd].

## Important APIs, Types, and Functions

This YAML is consumed as data by the syzkaller `ifuzz` RISC-V generator rather than exporting callable code. The important schema fields are `$schema`, `kind`, `name`, `long_name`, `description`, `definedBy`, `assembly`, `format` or `encoding`, `access`, `data_independent_timing`, `pseudoinstructions`, `operation()`, and optional `sail()`. For this file, the instruction name is `mop.r.n`, long name is `May-be-operation (1 source register)`, access is `s=always, u=always, vs=always, vu=always`, data-independent timing is `false`, and pseudoinstruction metadata is when `n == 0` to `mop.r.0`; when `n == 1` to `mop.r.1`; when `n == 2` to `mop.r.2`; when `n == 3` to `mop.r.3`; when `n == 4` to `mop.r.4`; when `n == 5` to `mop.r.5`; when `n == 6` to `mop.r.6`; when `n == 7` to `mop.r.7`; when `n == 8` to `mop.r.8`; when `n == 9` to `mop.r.9`; when `n == 10` to `mop.r.10`; when `n == 11` to `mop.r.11`; when `n == 12` to `mop.r.12`; when `n == 13` to `mop.r.13`; when `n == 14` to `mop.r.14`; when `n == 15` to `mop.r.15`; when `n == 16` to `mop.r.16`; when `n == 17` to `mop.r.17`; when `n == 18` to `mop.r.18`; when `n == 19` to `mop.r.19`; when `n == 20` to `mop.r.20`; when `n == 21` to `mop.r.21`; when `n == 22` to `mop.r.22`; when `n == 23` to `mop.r.23`; when `n == 24` to `mop.r.24`; when `n == 25` to `mop.r.25`; when `n == 26` to `mop.r.26`; when `n == 27` to `mop.r.27`; when `n == 28` to `mop.r.28`; when `n == 29` to `mop.r.29`; when `n == 30` to `mop.r.30`; when `n == 31` to `mop.r.31`.

## Control Flow

Generation control flow starts when the ifuzz tooling loads this descriptor under `gen/inst`, validates it against `inst_schema.json`, evaluates `definedBy` for the selected ISA profile, and maps `xd, xs1` operands to either inherited format fields or explicit encoding variables. Encoding information is match pattern `1-00--0111-------100-----1110011` with variables n@30|27-26|21-20, xs1@19-15, xd@11-7. Variable bindings are n@30|27-26|21-20, xs1@19-15, xd@11-7. The semantic lane then attaches the `operation()` block (present) and `sail()` block (absent) to generated execution or reference-model material. Unless redefined by another extension, this instructions simply writes 0 to X[xd]. The encoding allows future extensions to define them to read X[xs1], as well as write X[xd]. The operation body updates an integer register.

## State and Persistence Behavior

The descriptor itself is static repository data and has no runtime persistence. When generated into an executor or model, its architectural state surface is: integer register file updates, microarchitectural hint or cache/fetch ordering state. Any persistent behavior comes from generated tables or compiled artifacts that embed this YAML content, not from the YAML file at runtime.

## Dependencies and Integration Points

Dependencies are inst_schema.json; explicit encoding-match parser; extension availability expression `Zimop`. Integration points are the RISC-V instruction YAML loader, schema validator, assembler/disassembler table generation, random instruction selection in syzkaller ifuzz, semantic model generation from `operation()`/`sail()`, and extension-profile filtering for `Zimop`. The source path and mirrored research path are significant because the research cron reconciler splits grouped reports by exact source path.

## Risks and Edge Cases

data-independent timing is explicitly false or not guaranteed; bit-field locations and immediate transforms must remain synchronized with the ISA encoding.

## Test Signals

schema validation against inst_schema.json; generator round-trip checks for assembly operands and binary encoding; semantic differential tests against the Sail snippet or ISA pseudocode; pseudoinstruction expansion tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zimop/mop.r.n.yaml -->
