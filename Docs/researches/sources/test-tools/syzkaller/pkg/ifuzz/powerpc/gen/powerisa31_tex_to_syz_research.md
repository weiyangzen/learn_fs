# sources/test-tools/syzkaller/pkg/ifuzz/powerpc/gen/powerisa31_tex_to_syz

## Purpose

`powerisa31_tex_to_syz` is a Python 3 code generator for syzkaller's PowerPC instruction fuzzer metadata using the Power ISA 3.1 LaTeX sources instead of PDF text extraction. It walks an ISA source directory, parses instruction syntax and layout macros, identifies privileged mnemonics from the appendix mnemonic table, and emits Go code for package `generated` that registers `[]*powerpc.Insn`.

Compared with the ISA 3.0 PDF generator, this script is structured around LaTeX macro data. That removes many page-offset and table-splitting concerns, but still requires detailed knowledge of the ISA document macro conventions.

## Important APIs, types, and functions

The key helper functions are:

- `read_file(fname)`: returns a file as a list of lines without trailing newline records, or `[]` if the path is not readable according to `os.access`.
- `get_layouts(layout_file)`: parses `ilayouts.tex` layout macro definitions. It carries the preceding `%` comment as the bit layout description and returns a mapping from layout macro name to `(positions, names)`, where positions are bit widths and names are fixed field labels or `None` placeholders.
- `complete_layout(layout, insn_layout)`: expands unnamed placeholders in a layout using the arguments from a concrete instruction layout macro invocation. It normalizes special text such as `any value\textsuperscript{*}` and repeated slashes.
- `find_insns(tex_file, layouts)`: extracts instruction mnemonics and layouts from a single `.tex` file. It tracks `\instrsyntax{...}` lines, then associated `\layout...{...}` macro calls, and returns a map from instruction name to one or two layout tuples.
- `collect_priv(tex_file, insns)`: parses `Appendices/inst-mnem.tex`, merges rows between `\hline`, splits LaTeX table columns, and returns instruction names marked privileged by relevant privilege cells.
- `generate_go(insns, priv)`: emits Go struct literals for all parsed instructions. It contains nested helpers `ppcmask()` and `generate_opcode()` to convert parsed field layouts into opcode, mask, and field metadata.

The script also creates pretty-printers `pp` and `pe`, although only `pe` is materially used for stderr diagnostics.

## Control flow

The script expects `sys.argv[1]` to be the root of an ISA LaTeX source tree. It parses `isa_dir + "/ilayouts.tex"` first, then runs `find` for every `*.tex` file under the ISA directory. Each file is passed to `find_insns()`, and all instruction maps are merged with `insns.update(...)`.

`find_insns()` maintains current instruction syntax and layout state. When it sees `\instrsyntax{...}`, it flushes any previous instruction-plus-layout group. Layout macro calls are resolved through `layouts[...]`, expanded with `complete_layout()`, and accumulated. `add_insns()` then converts each syntax line into a map entry. It supports one or two layouts per instruction and records default one-bit field values from syntax suffixes like `(OE=0 Rc=1)`.

After parsing all instruction sources, the script prints a generated Go file:

1. `// Code generated ...`
2. `//go:build !codeanalysis` and legacy `// +build !codeanalysis`
3. `package generated`
4. import of `github.com/google/syzkaller/pkg/ifuzz/powerpc`
5. `init()` calling `powerpc.Register(insns)`
6. `var insns = []*powerpc.Insn{ ... }`

`generate_go()` sorts instruction names, calculates opcode and mask for the primary layout, optionally calculates `OpcodeSuffix`, `MaskSuffix`, and `FieldsSuffix` for a second layout, appends `Priv: true` for privileged instructions, and prints each record. It writes the processed instruction count to stderr at the end.

## State and persistence behavior

The generator does not persist state itself. It reads the ISA source tree and writes generated Go to stdout plus diagnostics to stderr. Callers are responsible for redirecting stdout to the checked-in generated file.

In-memory state includes the layout map, the instruction map, temporary parser state inside `find_insns()`, and the privileged instruction list. Merging instruction maps with `insns.update()` means later `.tex` files can overwrite an instruction with the same name if duplicates exist in `find` traversal order.

## Dependencies and integration points

Runtime dependencies are Python standard libraries `re`, `os`, `sys`, `pprint`, and `subprocess`, plus the external `find` command. Input dependencies are the Power ISA 3.1 LaTeX tree, especially `ilayouts.tex`, instruction `.tex` files containing `\instrsyntax` and `\layout...` macros, and `Appendices/inst-mnem.tex`.

The generated output integrates with syzkaller's PowerPC ifuzz layer through these Go API expectations:

- `powerpc.Register(insns)` accepts generated instruction metadata.
- `powerpc.Insn` has fields `Name`, `Opcode`, `Mask`, `Fields`, optional suffix opcode/mask/fields, and `Priv`.
- `powerpc.InsnField` and `powerpc.InsnBits` encode operand bit ranges with Power ISA bit numbering.

The generator has PowerPC-specific fixups for MD-form rotate fields and SPR numbering. For rotate/shift instructions such as `rldcl`, `rldic`, `rldicl`, `rldimi`, `rldcr`, and `rldicr`, six-bit `me` and `mb` fields are split into `(21,5)` and `(26,1)`. For `mfspr` and `mtspr`, the ten-bit `spr` field is reordered into `(16,5)` and `(11,5)`.

## Risks and maintenance notes

The parser depends on ISA LaTeX conventions rather than a formal AST. It assumes layout bit comments immediately precede `\newcommand{\layout...}` definitions and that those comments can be converted into bit widths and optional field names by splitting on spaces. It also assumes instruction syntax and layout macros appear close enough for the simple state machine in `find_insns()`.

`read_file()` checks readability with `os.access(fname, os.O_RDONLY)`, using a file-open flag as the mode argument rather than the more conventional `os.R_OK`. On typical systems this still evaluates as a permission bit value, but it is subtle and can obscure intent.

The external `find` traversal order is not explicitly sorted. Final Go output is sorted by instruction name, but duplicate mnemonic resolution depends on traversal order before sorting. Missing layout macros, more than two layouts, malformed default-value suffixes, and unexpected appendix table shapes are fatal or silently incomplete depending on where they occur.

Field handling is intentionally specialized. Fixed slash fields are forced to zero, numeric fields become opcode bits, empty names are ignored, default field values are only extracted for one-character numeric assignments, and only known split-field encodings receive custom handling. New ISA macro forms may require generator updates.

## Test signals

Primary validation is that generated Go compiles and that `go test` succeeds for the PowerPC ifuzz packages that consume `generated`. The stderr "Processed N instructions" count should be stable for a fixed ISA source revision and can be compared with a golden count.

Additional useful tests include checking that generated output is gofmt-stable, contains expected privileged instructions, includes suffix metadata for two-layout instructions, and has no zero-length field ranges. Fixture tests around `get_layouts()`, `complete_layout()`, and `generate_opcode()` would catch the most likely parser drift without requiring the full ISA tree.
