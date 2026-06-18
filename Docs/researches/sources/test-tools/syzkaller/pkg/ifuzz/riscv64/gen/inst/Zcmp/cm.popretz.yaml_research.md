<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zcmp/cm.popretz.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zcmp/cm.popretz.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zcmp/cm.popretz.yaml` is a RISC-V ifuzz instruction descriptor for `cm.popretz` in the `Zcmp` extension family. It declares a `instruction` with assembly form `reg_list, stack_adj` and extension gating `Zcmp`. Destroys a stack frame: load `ra` and 0 to 12 saved registers from the stack frame, deallocate the stack frame, move zero to `a0`, return to `ra`. This instruction pops (loads) the registers in `reg_list` from stack memory, and then adjusts the stack pointer by `stack_adj`, move zero to `a0` and then return to `ra`. Restrictions on stack_adj: * it must be enough to store all of the listed registers * it must be a multiple of 16 (bytes): ** for RV32 the allowed values are: 16, 32, 48, 64, 80, 96, 112 ** for RV64 the allowed values are: 16, 32, 48, 64, 80, 96, 112, 128, 144, 160

## Important APIs, Types, and Functions

This YAML is consumed as data by the syzkaller `ifuzz` RISC-V generator rather than exporting callable code. The important schema fields are `$schema`, `kind`, `name`, `long_name`, `description`, `definedBy`, `assembly`, `format` or `encoding`, `access`, `data_independent_timing`, `pseudoinstructions`, `operation()`, and optional `sail()`. For this file, the instruction name is `cm.popretz`, long name is `Destroy function call stack frame, move zero to `a0` and return to `ra``, access is `s=always, u=always, vs=always, vu=always`, data-independent timing is `not specified`, and pseudoinstruction metadata is none.

## Control Flow

Generation control flow starts when the ifuzz tooling loads this descriptor under `gen/inst`, validates it against `inst_schema.json`, evaluates `definedBy` for the selected ISA profile, and maps `reg_list, stack_adj` operands to either inherited format fields or explicit encoding variables. Encoding information is match pattern `10111100------10` with variables rlist@7-4, spimm@3-2. Variable bindings are rlist@7-4 (not=[0, 1, 2, 3]), spimm@3-2 (left_shift=4). The semantic lane then attaches the `operation()` block (present) and `sail()` block (absent) to generated execution or reference-model material. Destroys a stack frame: load `ra` and 0 to 12 saved registers from the stack frame, deallocate the stack frame, move zero to `a0`, return to `ra`. This instruction pops (loads) the registers in `reg_list` from stack memory, and then adjusts the stack pointer by `stack_adj`, move zero to `a0` and then return to `ra`. Restrictions on stack_adj: * it must be enough to store all of the listed registers * it must be a multiple of 16 (bytes): ** for RV32 the allowed values are: 16, 32, 48, 64, 80, 96, 112 ** for RV64 the allowed values are: 16, 32, 48, 64, 80, 96, 112, 128, 144, 160; multi-register stack-frame restoration and stack-pointer adjustment. The operation body reads architectural memory, updates an integer register, consults or updates CSR state, can raise architectural exceptions, has illegal-instruction gating.

## State and Persistence Behavior

The descriptor itself is static repository data and has no runtime persistence. When generated into an executor or model, its architectural state surface is: integer register file updates, CSR reads or writes, architectural memory reads, architectural exception state. Any persistent behavior comes from generated tables or compiled artifacts that embed this YAML content, not from the YAML file at runtime.

## Dependencies and Integration Points

Dependencies are inst_schema.json; explicit encoding-match parser; extension availability expression `Zcmp`. Integration points are the RISC-V instruction YAML loader, schema validator, assembler/disassembler table generation, random instruction selection in syzkaller ifuzz, semantic model generation from `operation()`/`sail()`, and extension-profile filtering for `Zcmp`. The source path and mirrored research path are significant because the research cron reconciler splits grouped reports by exact source path.

## Risks and Edge Cases

bit-field locations and immediate transforms must remain synchronized with the ISA encoding; address alignment, translation, exception ordering, and memory side effects are easy regression points; compressed encodings have narrow operand sets and reserved encodings that should not be fuzzed as legal instructions.

## Test Signals

schema validation against inst_schema.json; generator round-trip checks for assembly operands and binary encoding; semantic differential tests against the Sail snippet or ISA pseudocode; memory alignment and exception-order tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zcmp/cm.popretz.yaml -->
