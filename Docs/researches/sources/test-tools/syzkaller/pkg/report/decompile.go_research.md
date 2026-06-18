# sources/test-tools/syzkaller/pkg/report/decompile.go

Purpose: Converts raw opcode bytes into human-readable assembly descriptions by invoking target `objdump`.

Important APIs and types: `DecompilerFlagMask` and `FlagForceArmThumbMode` control decompilation. `DecompiledOpcode` records offset, bad-instruction flag, instruction text, and full objdump line. `DecompileOpcodes` is the main entry. Internal helpers are `objdumpExecutor`, `objdumpParseOutput`, and `objdumpBuildArgs`.

Control flow: `DecompileOpcodes` builds architecture-specific objdump arguments, writes raw bytes to a temp file, runs `target.Objdump` with a 10-second timeout, parses assembly lines, and errors if non-empty input yields no instructions. `objdumpParseOutput` scans lines with a regexp, parses hex offsets, marks `(bad)` instructions, and trims trailing whitespace. `objdumpBuildArgs` sets binary disassembly mode and architecture flags for arm64, arm, i386, amd64, mips64le, ppc64le, s390x, and riscv64.

State and persistence: Creates and removes a temporary file. No persistent state.

Dependencies and integration: Used by report parsing paths that decompile kernel opcode bytes, especially Linux report code outside this shard. Depends on `osutil.RunCmd` and `targets.Target`.

Risks: Requires a usable target objdump in PATH/config. Raw objdump output parsing is regex-sensitive. Unsupported architectures return errors. Temporary file creation/writing errors block decompilation.

Test signals: `decompile_test.go` validates objdump output parsing including `(bad)` instruction detection.
