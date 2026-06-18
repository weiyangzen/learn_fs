# sources/test-tools/syzkaller/pkg/symbolizer/addr2line_test.go

## Purpose

This test file validates the `symbolize` and `parse` protocol against a stubbed addr2line stream, including batching and high-volume writes.

## Important APIs, Types, And Functions

`TestParse` defines address-to-response fixtures with expected `Frame` slices. It uses `os.Pipe` pairs to simulate addr2line stdin/stdout, runs a goroutine that responds to PC lines, and calls `symbolize` repeatedly.

## Control Flow, State, Dependencies, And Integration

The test first symbolises each PC individually, then splits the same PC list into two groups at every boundary, then sends 10,000 PCs to exercise pipe overflow avoidance. It uses `reflect.DeepEqual` against exact frames.

## Risks And Test Signals

Coverage includes unknown `??` frames, line zero normalization, inline flag assignment, file-line suffixes such as discriminator text, and sentinel behavior. It catches deadlocks in the goroutine/flush protocol. It does not start a real `addr2line` binary, so toolchain discovery and subprocess lifecycle are covered elsewhere only indirectly.
