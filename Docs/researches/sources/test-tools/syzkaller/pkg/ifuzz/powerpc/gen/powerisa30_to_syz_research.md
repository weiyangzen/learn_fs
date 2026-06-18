# sources/test-tools/syzkaller/pkg/ifuzz/powerpc/gen/powerisa30_to_syz

## Purpose

`powerisa30_to_syz` is a Python 3 code generator for syzkaller's PowerPC instruction fuzzer metadata. It consumes a Power ISA 3.0 PDF and emits Go source for package `generated`, registering a sorted `[]*powerpc.Insn` table with opcode, mask, privilege, and operand field metadata. The generated Go is intended for `github.com/google/syzkaller/pkg/ifuzz/powerpc` and is excluded when the `codeanalysis` build tag is active.

The generator is tailored to the formatting of a specific Power ISA 3.0 PDF. It extracts the "Instruction Set Sorted by Opcode" table, resolves each variable instruction to its detailed instruction-format page, reconstructs fixed opcode bits and operand bit ranges, and prints Go struct literals.

## Important APIs, types, and functions

This file is an executable script rather than an importable module, but its major internal APIs are:

- `add_stat(m, s)` and `add_fmt_ins(m, fmt, ins)`: small aggregation helpers for stderr summary statistics by format, privilege, mode, and mnemonic.
- `read_pdf_page(pnum, store=False)`: page extraction and normalization layer. It calls an external `pdftotext`, caches page text in `pagecache`, optionally splits two-column instruction pages into logical rows, removes empty and `[Phased-Out]` lines, writes debug extraction data to `outp`, and returns normalized text lines.
- `find_pdf_pagenumber_offset()`: scans physical PDF pages 15 through 99 to discover the logical-to-physical page offset and the logical page range containing the sorted opcode table.
- `add_mode_priv(mode, priv)`: converts Power ISA privilege/mode text into a Go `Priv: true` field when privilege contains `P` or `H`.
- `ppcmask(val, s, l)`: maps Power ISA bit numbering, where bit 0 is the most significant bit, to a 32-bit integer mask/value position.
- `do_sorted_opcodes(fmt_map, ins_stat)`: the core generator. It parses opcode summary rows, resolves detailed instruction layouts, applies manual fixups, builds `Opcode`, `Mask`, and `[]powerpc.InsnField` literals, prints sorted instruction records, and returns the emitted instruction count.

Global constants and state are also important. `pdf2txt` is hard-coded to `/home/aik/xpdf-4.03/build/xpdf/pdftotext`; `isa_pdf` is `sys.argv[1]`; `isa_pagenum_correction` contains mnemonic-specific page corrections for known PDF index drift; `pagecache` memoizes normalized pages; and the global file handle `f = open("outp", "w+")` receives extraction traces.

## Control flow

The script starts by reading the ISA PDF path from `sys.argv[1]`. If `sys.argv[2:5]` are present, it treats them as explicit `pageoffset`, `opcodes_first_page`, and `opcodes_last_page`; otherwise it derives those values with `find_pdf_pagenumber_offset()`.

Generation then prints the Go header, build tags, package declaration, import, `init` registration hook, and the start of `var insns = []*powerpc.Insn{`. `do_sorted_opcodes()` drives the body:

1. Read each sorted-opcode logical page translated through `pageoffset`.
2. Locate the table header offsets for `Privilege3` and `Mode Dep4`.
3. Match opcode rows with a large regular expression that captures six opcode bit groups, instruction format, book, page number, mnemonic, and ISA version.
4. Convert bit pattern strings into a base opcode mask and opcode value. Dots become variable bits, slashes become zero-like separators, and fixed `0`/`1` bits become mask/value bits.
5. For fully fixed 32-bit rows, emit an instruction immediately with `Mask: 0xFFFFFFFF`.
6. For variable layouts, apply mnemonic page corrections, read the detailed page with `store=True`, locate the mnemonic syntax and following bit-grid rows, and infer field names plus bit positions.
7. Apply special-case corrections for malformed PDF layouts, including `addpcis`, `darn`, `copy`, `paste.`, vector compare missing offsets, concatenated field labels such as `AXBXTX`, and MD-form split fields.
8. Iterate over each instruction variant line, including forms with fixed default bits like `(OE=1 Rc=0)`, then build opcode/mask bits and operand field ranges.
9. Validate overlapping bit coverage with `check_bitmap`, merge the opcode-summary mask into the detailed mask, warn when calculated opcode bits fall outside the mask, and add `Priv: true` when needed.
10. Sort and print all generated Go instruction literals.

After generation, the script closes the Go slice, prints total instruction counts and per-stat summaries to stderr, and exits through normal process termination. Error paths call `sys.exit()` when required PDF structure cannot be found or when unsupported layouts are encountered.

## State and persistence behavior

The generator has process-local parsing state in `pagecache`, `ins_stat`, and `fmt_map`. It has two persistent side effects: generated Go is written to stdout, and verbose extraction/debug output is written to stderr plus a local file named `outp` in the current working directory. It does not update repository files directly; build systems are expected to redirect stdout into the generated Go file.

The script relies on deterministic PDF contents and a deterministic external text extractor. Because `read_pdf_page()` caches by page number string, repeated detailed-page reads reuse normalized text and avoid repeated `pdftotext` calls.

## Dependencies and integration points

Runtime dependencies are Python standard libraries `re`, `sys`, `pprint`, and `subprocess`, plus the external Xpdf `pdftotext` binary. The input dependency is a Power ISA 3.0 PDF matching the expected table layout. The output dependency is syzkaller's `pkg/ifuzz/powerpc` package, specifically the Go symbols `powerpc.Register`, `powerpc.Insn`, `powerpc.InsnField`, and `powerpc.InsnBits`.

The emitted Go integrates through an `init()` function:

- `package generated`
- `import "github.com/google/syzkaller/pkg/ifuzz/powerpc"`
- `powerpc.Register(insns)`

That means importing the generated package registers the instruction metadata into the ifuzz PowerPC backend.

## Risks and maintenance notes

The largest risk is PDF-layout fragility. Parsing depends on exact text extraction geometry, table headings, page footers, field names, and mnemonic formatting. Several manual fixups already show known breakage points, and new PDFs or `pdftotext` versions can shift offsets or concatenate labels differently.

The hard-coded absolute `pdftotext` path is non-portable and makes the script environment-specific. The local `outp` debug file can overwrite an unrelated file in the caller's working directory. Error handling is intentionally fail-fast, but many failures happen after partially writing Go to stdout, so callers should generate to a temporary file before replacing checked-in output.

Parsing risks include broad bare `except` blocks, direct integer parsing of layout fields, reliance on `priv_off` and `mode_off` being initialized by a header line, and special handling for only known duplicated or split fields. The script also treats privilege as true for any `P` or `H` in the extracted privilege cell, which is simple but depends on the source table encoding.

## Test signals

Useful validation signals are generated-code compilation, successful `go test` coverage for `pkg/ifuzz/powerpc` and packages importing `generated`, and comparison of generated instruction count/stat summaries against known-good runs. The script's own stderr output is also a test signal: missing pages, unsupported layouts, bit overlaps, wrong field lengths, and opcode/mask warnings indicate generator or input drift.

Golden-output testing would be valuable because the generator is deterministic for a fixed PDF and `pdftotext` version. A robust test should redirect stdout to a temporary Go file, verify it formats and builds, and ensure no unexpected stderr warnings appear.
