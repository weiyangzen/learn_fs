# sources/test-tools/syzkaller/pkg/cover/backend/dwarf.go

Purpose: implements the shared DWARF-backed coverage backend used by ELF and Mach-O frontends. It discovers sanitizer callback PCs, associates them with symbols and compile units, normalizes source paths, and lazily symbolizes PCs into source frames.

Important APIs/types/functions: `dwarfParams` injects object-format-specific readers; `Arch` describes call scanning for amd64, arm64, and s390x; `makeDWARF` wraps `makeDWARFUnsafe` with panic recovery for DWARF parser failures; `processModule`, `buildSymbols`, `readTextRanges`, `rustRanges`, `symbolizeModule`, `symbolize`, `readCoverPoints`, `objdump`, `CleanPath`, and `archCallInsn` form the main pipeline. `symbolInfo`, `pcRange`, and `Result` carry intermediate symbol/callback state.

Control flow: `makeDWARFUnsafe` launches one goroutine per kernel/module object, each reading symbols, coverage callbacks, text ranges, and compile units. Results are merged, sorted, deduplicated by symbol start, assigned to compile units, path-cleaned, and exposed through `backend.Impl`. Callback discovery prefers direct instruction scanning on supported arches, uses relocation scanning for modules, and falls back to `objdump` on other arches. Symbolization batches PCs by module and runs bounded parallel addr2line instances to control memory.

State and persistence: all state is in-memory (`Impl`, symbolized flags, interner, callback point slices). No persistent writes occur. The interner and `Symbol.Symbolized` flag make repeated symbolization incremental.

Dependencies and integration: depends on Go `debug/dwarf` plus syzkaller `symbolizer`, `mgrconfig`, `vminfo`, `targets`, and object-format frontends. It integrates upward through `backend.Make` and `pkg/cover.ReportGenerator`.

Risks: DWARF5/parser panics are converted to errors but still block coverage. Path normalization is heuristic, especially Android split builds and out-of-tree modules. `buildSymbols` drops symbols without PCs or compile-unit range matches. Compiler KCOV breakage disables strict precision for GCC versions below 14 or unparsable GCC strings. Objdump parsing is architecture-string fragile and intentionally slower.

Test signals: `dwarf_test.go` validates compiler KCOV detection, Android path cleaning, and call-target decoding for arm64/amd64. Broader report tests exercise this backend through compiled test binaries.
