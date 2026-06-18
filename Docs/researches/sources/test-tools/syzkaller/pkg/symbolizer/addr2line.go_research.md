# sources/test-tools/syzkaller/pkg/symbolizer/addr2line.go

## Purpose

`addr2line.go` implements the `Symbolizer` backend using a persistent `addr2line` subprocess per binary. It translates program counters into function/file/line frames, including inline frames.

## Important APIs, Types, And Functions

`addr2Line` stores a target, subprocess map, and string interner. `Symbolize` obtains a subprocess and calls `symbolize`. `Close` closes pipes, kills subprocesses, and waits. `getSubprocess` invokes `target.Addr2Line()` and starts `addr2line -afi -e <bin>`. `symbolize` writes PCs plus a sentinel invalid PC, reads parsed frames in a goroutine, and returns combined frames. `parse` consumes addr2line output into `Frame` values.

## Control Flow, State, Dependencies, And Integration

State persists across calls in `subprocs` and `Interner`, reducing process startup and string allocation. Parsing treats line `0` as unknown (`-1`), drops `??` or invalid frames, and marks the last frame for a PC as non-inline. Dependencies include `os/exec`, `bufio.Scanner`, `osutil.Command`, and target toolchain metadata. This is the primary implementation returned by `symbolizer.Make`.

## Risks And Test Signals

The implementation is not explicitly synchronized; concurrent `Symbolize` calls on the same `addr2Line` would race on pipes and maps. Scanner token limits can affect very long symbol lines. If `addr2line` exits or emits unexpected format, errors propagate. `addr2line_test.go` covers parsing, inline frames, discriminator suffixes, unknown PCs, batching, and pipe backpressure.
