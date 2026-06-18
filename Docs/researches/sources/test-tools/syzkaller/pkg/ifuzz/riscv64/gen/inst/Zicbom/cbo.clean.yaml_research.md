<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zicbom/cbo.clean.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zicbom/cbo.clean.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zicbom/cbo.clean.yaml` is a RISC-V ifuzz instruction descriptor for `cbo.clean` in the `Zicbom` extension family. It declares a `instruction` with assembly form `(xs1)` and extension gating `Zicbom`. Cleans an entire cache block globally throughout the system. Exactly what happens is coherence protocol-dependent, but in general it is expected that after this operation(): * The cache block will be in the clean (not dirty) state in any coherent cache holding a valid copy of the line. * The data will be cleaned to a point such that an incoherent load can observe the cleaned data. `cbo.clean` is ordered by `FENCE` instructions but not `FENCE.I` or `SFENCE.VMA`. <%- if CACHE_BLOCK_SIZE.bit_length > [PMP_GRANULARITY, PMA_GRANULARITY].min -%> Both PMP and PMA access control must be the same for all bytes in the block; otherwise, `cbo.clean` has UNSPECIFIED behavior. <%- end -%> Clean operations are treated as stores for page and access permissions. If permission checks fail, one of the following exceptions will occur: <%- if ext?(:H) -%> * `Store/AMO Guest-Page Fault` if virtual memory translation fails during G-stage translation. <%- end -%> * `Store/AMO Page Fault` if virtual memory translation fails <% if ext?(:H) %>when V=0 or during VS-stage translation<% end %> * `Store/AMO Access Fault` if a PMP or PMA access check fails <%- if CACHE_BLOCK_SIZE.bit_length <= [PMP_GRANULARITY, PMA_GRANULARITY].min -%> Because cache blocks are naturally aligned and always fit in a single PMP or PMA regions, the PMP and PMA access checks only need to check a single address in the line. <%- end -%> CBO operations never raise a misaligned address fault.

## Important APIs, Types, and Functions

This YAML is consumed as data by the syzkaller `ifuzz` RISC-V generator rather than exporting callable code. The important schema fields are `$schema`, `kind`, `name`, `long_name`, `description`, `definedBy`, `assembly`, `format` or `encoding`, `access`, `data_independent_timing`, `pseudoinstructions`, `operation()`, and optional `sail()`. For this file, the instruction name is `cbo.clean`, long name is `Cache Block Clean`, access is `m=always, s=sometimes, u=sometimes, vs=sometimes, vu=sometimes`, data-independent timing is `not specified`, and pseudoinstruction metadata is none.

## Control Flow

Generation control flow starts when the ifuzz tooling loads this descriptor under `gen/inst`, validates it against `inst_schema.json`, evaluates `definedBy` for the selected ISA profile, and maps `(xs1)` operands to either inherited format fields or explicit encoding variables. Encoding information is match pattern `000000000001-----010000000001111` with variables xs1@19-15. Variable bindings are xs1@19-15. The semantic lane then attaches the `operation()` block (empty) and `sail()` block (absent) to generated execution or reference-model material. Cleans an entire cache block globally throughout the system. Exactly what happens is coherence protocol-dependent, but in general it is expected that after this operation(): * The cache block will be in the clean (not dirty) state in any coherent cache holding a valid copy of the line. * The data will be cleaned to a point such that an incoherent load can observe the cleaned data. `cbo.clean` is ordered by `FENCE` instructions but not `FENCE.I` or `SFENCE.VMA`. <%- if CACHE_BLOCK_SIZE.bit_length > [PMP_GRANULARITY, PMA_GRANULARITY].min -%> Both PMP and PMA access control must be the same for all bytes in the block; otherwise, `cbo.clean` has UNSPECIFIED behavior. <%- end -%> Clean operations are treated as stores for page and access permissions. If permission checks fail, one of the following exceptions will occur: <%- if ext?(:H) -%> * `Store/AMO Guest-Page Fault` if virtual memory translation fails during G-stage translation. <%- end -%> * `Store/AMO Page Fault` if virtual memory translation fails <% if ext?(:H) %>when V=0 or during VS-stage translation<% end %> * `Store/AMO Access Fault` if a PMP or PMA access check fails <%- if CACHE_BLOCK_SIZE.bit_length <= [PMP_GRANULARITY, PMA_GRANULARITY].min -%> Because cache blocks are naturally aligned and always fit in a single PMP or PMA regions, the PMP and PMA access checks only need to check a single address in the line. <%- end -%> CBO operations never raise a misaligned address fault; cache-block address computation and cache maintenance side effects. The operation block is empty, so this descriptor currently contributes metadata and encoding more than executable pseudocode.

## State and Persistence Behavior

The descriptor itself is static repository data and has no runtime persistence. When generated into an executor or model, its architectural state surface is: microarchitectural hint or cache/fetch ordering state. Any persistent behavior comes from generated tables or compiled artifacts that embed this YAML content, not from the YAML file at runtime.

## Dependencies and Integration Points

Dependencies are inst_schema.json; explicit encoding-match parser; extension availability expression `Zicbom`. Integration points are the RISC-V instruction YAML loader, schema validator, assembler/disassembler table generation, random instruction selection in syzkaller ifuzz, semantic model generation from `operation()`/`sail()`, and extension-profile filtering for `Zicbom`. The source path and mirrored research path are significant because the research cron reconciler splits grouped reports by exact source path.

## Risks and Edge Cases

empty semantic body can leave downstream simulators or documentation generators without executable behavior; bit-field locations and immediate transforms must remain synchronized with the ISA encoding; address alignment, translation, exception ordering, and memory side effects are easy regression points.

## Test Signals

schema validation against inst_schema.json; generator round-trip checks for assembly operands and binary encoding; memory alignment and exception-order tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zicbom/cbo.clean.yaml -->
