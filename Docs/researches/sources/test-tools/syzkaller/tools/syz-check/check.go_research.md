<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-check/check.go -->
# sources/test-tools/syzkaller/tools/syz-check/check.go

## Purpose

Static checker for syzkaller syscall descriptions against kernel DWARF structs and netlink policy data.

## Important APIs, Types, and Functions

Functions `check`, `writeWarnings`, `checkStruct`, `parseDescriptions`, `checkNetlink*`; warning constants; `nlaPolicy` layout.

## Control Flow

For each `-obj-arch`, compiles sys descriptions, optionally parses vmlinux DWARF and compares struct sizes/fields/offsets/bitfields, optionally reads amd64 rodata netlink policies and compares nlattr type/size/range, writes grouped `.warn` files and removes stale ones.

## State and Persistence Behavior

Persists `sys/<os>/*.warn`; in-memory AST/prog/DWARF/symbol warning state.

## Dependencies and Integration Points

Depends on syzkaller compiler/prog, vmlinux DWARF, ELF rodata symbols, target consts; netlink check is amd64-specific.

## Risks and Edge Cases

Known false positives for unions, overlays, varlen/split policies; `nlaPolicy` layout is kernel/64-bit sensitive.

## Test Signals

Run with documented multi-arch vmlinux files and inspect `.warn` diffs; unit fixtures for struct/netlink mismatches.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-check/check.go -->
