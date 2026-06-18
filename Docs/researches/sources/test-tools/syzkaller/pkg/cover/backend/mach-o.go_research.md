# sources/test-tools/syzkaller/pkg/cover/backend/mach-o.go

Purpose: supplies Mach-O/XNU reader hooks for the shared DWARF backend.

Important APIs/types/functions: `makeMachO`, `machoReadSymbols`, `machoReadTextRanges`, `machoReadTextData`, and `machoReadModuleCoverPoints`.

Control flow: `makeMachO` delegates to `makeDWARF` with Mach-O-specific readers. `machoReadSymbols` opens the binary, finds `__text`, sorts symbol table entries by value, estimates symbol ends from the next symbol or text end, records sanitizer callback indexes, and builds `Symbol` entries. `machoReadTextRanges` opens the companion `.dSYM/Contents/Resources/DWARF/<kernel>` file and feeds DWARF into `readTextRanges`. Text bytes come from `__text`. Module cover points are deliberately unimplemented.

State and persistence: no persisted state. `symbolInfo` and symbol slices are transient.

Dependencies and integration: uses Go `debug/macho`, syzkaller manager dirs and target metadata, and the shared DWARF pipeline. Intended for XNU-style coverage without module support.

Risks: symbol end estimation can be imprecise if non-function symbols interleave. `machoReadSymbols` adds `module.Addr` to start but stores unadjusted `symbEnd`, which is a subtle address-consistency risk. Opened Mach-O files are not explicitly closed in the current code. Module coverage returns an error.

Test signals: no direct tests in this subset. Coverage is indirect only if cross-platform report tests exercise Mach-O, which they currently do not on Linux-only build tags.
