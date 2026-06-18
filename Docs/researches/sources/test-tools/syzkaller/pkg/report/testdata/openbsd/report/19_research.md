# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/19

## Purpose

This OpenBSD fixture expects `malloc: free list modified: devbuf`. It captures an allocator integrity panic for a modified freelist object from the `devbuf` malloc type during BPF device open.

## Important APIs, Types, and Functions

Reporter behavior includes malloc-corruption title extraction, panic parsing, DDB transcript handling, and allocator diagnostic normalization. Kernel functions include `malloc`, `bpfopen`, `spec_open_clone`, `spec_open`, `VOP_OPEN`, `vn_open`, `doopenat`, `syscall`, and `Xsyscall`.

## Control Flow

The panic is raised by `malloc` after detecting that a freed object's poison value changed. The call path is opening a cloned special device for BPF, through VFS open helpers. DDB repeats the panic and trace, then records registers, process tables, malloc statistics, and pool state.

## State and Persistence Behavior

The fixture stores the object address, word index, object size, previous type `devbuf`, observed value, expected poison, process IDs, and allocator tables. The stable title uses the corruption class and malloc type, not addresses or poison values.

## Dependencies and Integration Points

This integrates OpenBSD allocator panic parsing with device-open/VFS stack capture. It also helps syzkaller group memory-corruption reports by allocator type when the direct corruptor may be earlier than the detecting allocation.

## Risks and Edge Cases

The detecting function `malloc` is generic, so the title must come from the diagnostic string. Including object addresses would make each run look unique. The parser must keep `bpfopen` and open-path frames as triage hints while not over-attributing the root cause.

## Test Signals

A passing test returns `malloc: free list modified: devbuf` and includes the `Data modified on freelist` panic plus the `bpfopen` open stack.
