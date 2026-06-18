<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/gen.sh -->
# sources/test-tools/strace/src/xlat/gen.sh

Purpose: Generator script for xlat input files; converts `.in` declarations into C header tables, optional m4 enum records, conditional macro definitions, and validation assertions.

Important APIs/types/functions:
- Shell functions: `usage`, `print_m4_record`, `cond_def`, `check_sort_order`, `print_xlat`, `print_xlat_pair`, `cond_xlat`, `gen_header`, `gen_make`, `gen_git`, `gen_m4_entry`, `main`
- Inputs are an xlat file or directory and an output directory; outputs generated headers and optional `.m4` records.

Control flow:
- parses command-line input/output, reads directives such as `#sorted`, `#value_indexed`, `#unconditional`, `#enum`, `#val_type`, and emits guarded `XLAT`/`XLAT_PAIR` rows
- checks sorted ordering with generated static assertions and emits fallback defines for constants with explicit numeric values

State and persistence behavior:
- uses shell-local counters/flags while processing each file; writes generated files under the requested output tree
- persistent artifacts are generated headers consumed by the build, not runtime state

Dependencies and integration points:
- requires POSIX shell utilities and the strace xlat input conventions
- integrates with generated `xlat/*.h`, `xlat.h`, build rules, and decoders using `printxval`/`printflags`

Risks:
- parser changes can affect every generated xlat table; directive handling must remain backward-compatible
- bad quoting or malformed `.in` rows can generate uncompilable headers or silently wrong fallback constants

Test signals:
- test signals include regenerating all xlat headers, compiling generated static assertions, and diffing generated output for deterministic changes
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/gen.sh -->
