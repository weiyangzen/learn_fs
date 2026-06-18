# sources/test-tools/syzkaller/tools/syz-trace2syz/proggen/proggen_test.go

## Purpose

`proggen_test.go` is the main regression suite for trace-to-program conversion. It verifies that representative strace snippets serialize to stable syzkaller programs.

## Important APIs, Types, and Functions

The file defines `TestParse`, a table of input/output cases, and uses `parser.ParseData`, `genProg`, `prog.GetTarget`, `targets.Linux`, `targets.AMD64`, and `prog.Prog.Serialize`. The blank `sys` import registers syscall descriptions needed by `prog.GetTarget`.

## Control Flow

The test initializes a Linux/amd64 target and fills its `ConstMap`. Each case trims the input trace, parses it into a trace tree, generates a program from the root PID trace, serializes the program, trims whitespace, and compares it to the expected text.

## State and Persistence Behavior

All state is test-local except for target description registration through the blank import. The test does not touch files, devices, or network resources.

## Dependencies and Integration Points

It exercises the parser, syscall target metadata, selector logic, resource cache, union generation, pointer allocation, and serialization format. It is the primary integration signal for `proggen` behavior.

## Risks and Test Signals

The suite is broad but example-driven; it does not cover all syscall descriptions or fatal error paths. Expected strings are sensitive to syscall description changes and allocator layout. High-value signals include resource reuse across `open`, `pipe`, and `inotify`, sockaddr family selection, ioctl selector choice, device-specific `openat` rewrites, endian parsing of network buffers, and default generation for omitted fields.
