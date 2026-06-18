# sources/test-tools/syzkaller/pkg/symbolizer/nm.go

## Purpose

`nm.go` reads ELF symbol tables and returns text or rodata symbols in a format syzkaller can use for symbol lookup and matching.

## Important APIs, Types, And Functions

`Symbol` stores `Addr` and `Size`. `ReadTextSymbols` and `ReadRodataSymbols` call `read`. `read` loads symbols, sorts them by descending address, and builds `map[string][]Symbol`. For text symbols, it recomputes size from the next lower symbol address to match Linux kernel symbol sizing. `load` opens an ELF file, reads symbols, filters invalid sections, text sections, or `.rodata`.

## Control Flow, State, Dependencies, And Integration

There is no persistent state. Dependencies are Go's `debug/elf`, `slices`, and `cmp`. Text detection uses section type/flags; rodata detection uses section name because some vmlinux `.rodata` flags resemble writable data. The output map supports duplicate symbol names.

## Risks And Test Signals

Risks include relying on regular ELF symbol tables only, section-name assumptions for rodata, and computed sizes for equal-address symbols. `nm_test.go` verifies duplicate text symbols and computed sizes on a checked-in ELF fixture.
