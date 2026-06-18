<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go

## Purpose

`gen.go` is the command-line generator that converts riscv-unified-db instruction YAML into syzkaller's `pkg/ifuzz/riscv64` generated instruction table. It walks a source `inst` tree, accepts instruction descriptors with 32-bit match patterns, translates fixed bits and variable bit ranges into `riscv64.Insn` values, serializes the resulting slice as Go code, and writes it atomically to the requested output path.

## Important APIs, Types, and Functions

`instYAML` is the narrow YAML projection used by this tool. It captures `kind`, `name`, `encoding.match`, `encoding.variables[].name`, `encoding.variables[].location`, and `access.u`/`access.vu`. `main` handles argument validation, directory walking, YAML reads, unmarshalling, filtering, output rendering, serialization, and atomic file write. `buildInsn` builds one `riscv64.Insn`. `parseLocations` expands single or split bit locations into `InsnField` entries. `parseRange` parses `hi-lo` location strings and returns the field start and length.

## Control Flow

The command requires exactly two arguments: the riscv-unified-db `spec/std/isa/inst` directory and an output Go file. `filepath.WalkDir` skips directories and non-YAML files. For each YAML file, it reads and unmarshals metadata; IO or YAML errors for individual files are ignored by returning nil from the walker. Non-`instruction` entries and match strings not exactly 32 characters long are skipped. `buildInsn` scans the 32-character match string from MSB to LSB, constructing opcode and mask bits for `0` and `1`, accepting `-` as variable, and rejecting any other character. Variables are parsed into fields, privilege is computed from U/VU access, and accepted instructions are appended.

After walking, `main` writes a generated Go preamble, imports the `riscv64` package dot-style, emits an `init` function that registers `insns_riscv64`, serializes the instruction slice with `serializer.Write`, and persists the result through `osutil.WriteFileAtomically`. It reports the generated instruction count on stderr.

## State and Persistence Behavior

State is local to the generator process: the `insns` slice, each decoded `instYAML`, and the output buffer. The only persistent side effect is replacing the output Go file atomically. The generated file becomes runtime registration state when compiled, because its `init` calls `Register`. The tool does not cache source scans and does not persist diagnostics for skipped or malformed YAML entries.

## Dependencies and Integration Points

The generator depends on the standard `bytes`, `fmt`, `io/fs`, `os`, `path/filepath`, and `strings` packages; `gopkg.in/yaml.v3`; and syzkaller packages `pkg/ifuzz/riscv64`, `pkg/osutil`, `pkg/serializer`, and `pkg/tool`. It integrates the riscv-unified-db schema with syzkaller's RISC-V ifuzz instruction model. Its output is expected to live in a generated package that registers with the runtime RISC-V instruction set.

## Risks and Edge Cases

Several failures are intentionally silent: unreadable YAML, unmarshal errors, non-instruction entries, bad match lengths, unsupported match characters, and bad variable locations are all skipped without per-file diagnostics. The parser only supports `hi-lo` ranges and `|`-separated range fragments; single-bit locations such as `5` are rejected. The `start` field is set to `hi`, matching the existing `riscv64.InsnField` convention, but any mismatch in downstream bit numbering would corrupt generated operands. The generator ignores YAML constraints like `left_shift`, `not`, reserved values, xlen requirements, and most extension metadata, so the generated fuzzer table is an encoding-oriented approximation rather than a full ISA validator.

## Test Signals

Useful tests should feed a temporary YAML tree containing valid 32-bit instructions, malformed match strings, split locations, non-instruction entries, unreadable or bad YAML files, and 16-bit compressed descriptors. Expected signals are generated instruction count, opcode/mask values, field names and ranges, privilege classification from access modes, and atomic output content containing `Register(insns_riscv64)`. Unit tests for `parseRange` and `parseLocations` should cover reversed ranges, missing hyphens, invalid numbers, and split field naming.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go -->
