# sources/test-tools/syzkaller/pkg/cover/backend/elf.go

Purpose: provides the ELF-specific implementation of the DWARF backend for Linux and other ELF kernels. It reads `.text`, symbol tables, relocations, DWARF ranges, compiler comments, and the Linux PC base.

Important APIs/types/functions: `makeELF`, `getTraceCallbackType`, `elfReadSymbols`, `elfReadTextRanges`, `elfReadTextData`, `elfReadModuleCoverPoints`, `elfGetCompilerVersion`, `elfReadTextSecRange`, `elfReadTextSec`, and `getLinuxPCBase`. Trace callback constants distinguish none, trace-pc, and trace-cmp callbacks.

Control flow: `makeELF` passes ELF reader functions to `makeDWARF`. `elfReadSymbols` scans ELF symbols, keeps function/notype symbols in `.text`, adjusts module starts by module load address, and records sanitizer callback symbol indexes/addresses. `elfReadTextRanges` reads DWARF and applies a KASLR PC fix when `.rela.text` suggests randomized-base debug ranges. `elfReadModuleCoverPoints` scans RELA sections for architecture call relocations into sanitizer callbacks.

State and persistence: no durable state; `symbolInfo` is populated for the active module. The returned section ranges and symbols feed `Impl`.

Dependencies and integration: uses Go `debug/elf`, syzkaller target metadata, module metadata, and manager kernel dirs. It is the primary frontend for Linux coverage and module support.

Risks: symbol filtering allows `STT_NOTYPE` to avoid nested range gaps but may include non-function labels. RELA parsing assumes little-endian `Rela64` and architecture relocation constants. Module symbol indexes are adjusted by `-1`, so malformed relocation tables could panic or misclassify. KASLR fix is approximate and may filter valid ranges.

Test signals: `elf_test.go` covers sanitizer callback name classification. `report_test.go` exercises no-debug-info, no-callback, PIE, and relocation scenarios through `makeELF`.
