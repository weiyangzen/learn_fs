# sources/test-tools/syzkaller/pkg/symbolizer/nm_test.go

## Purpose

This test validates text symbol extraction from the `testdata/nm.test.out` ELF fixture.

## Important APIs, Types, And Functions

`TestSymbols` calls `ReadTextSymbols`, checks total symbol-name count, verifies `barfoo` address/size, and verifies two `foobar` symbols with expected addresses and recomputed sizes. `symcmp` compares `Symbol` values.

## Control Flow, State, Dependencies, And Integration

The test depends on the fixture being a readable ELF file with a stable symbol table. It logs extracted symbols and uses fatal assertions for exact failures.

## Risks And Test Signals

The test catches regressions in duplicate-name handling and kernel-style size computation. It does not cover rodata extraction, missing/stripped symbol tables, invalid ELF files, or section filtering edge cases.
