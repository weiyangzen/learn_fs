# File Research: sources/os/linux/linux/io_uring/bpf_filter.c

## Purpose
Implements classic BPF filters for io_uring restrictions, allowing registered filters to allow or deny SQE opcodes based on an io_uring BPF context.

## Main Functions
- `io_uring_populate_bpf_ctx()`: fills `struct io_uring_bpf_ctx` from a request and optional opcode-specific PDU data.
- `__io_uring_run_bpf_filters()`: runs all registered filters for a request opcode; any zero return denies the request.
- `io_uring_check_cbpf_filter()`: validates and rewrites classic BPF instructions to a safe subset over the io_uring context.
- `io_new_bpf_filters()`, `io_free_bpf_filters()`, `io_put_bpf_filters()`: allocate/free reference-counted filter sets.
- `io_bpf_filter_clone()` and `io_bpf_filter_cow()`: clone filters for restrictions with copy-on-write.
- `io_bpf_filter_import()`: imports and validates userspace registration data, opcode, flags, reserved fields, filter length, and PDU size.
- `io_register_bpf_filter()`: creates a BPF program from userspace instructions and installs it into the per-opcode filter list.

## Important Design Points
- Filters are per opcode and stacked in a linked list; all filters must allow the request.
- `dummy_filter` represents an unconditional deny entry and is used by `IO_URING_BPF_FILTER_DENY_REST`.
- Filter sets are RCU-protected and reference counted.
- Copy-on-write avoids mutating cloned restriction filter sets directly.
- Accepted classic BPF is intentionally constrained: context loads, length loads, ALU, memory, and basic jumps; packet data access is not allowed.
- PDU size negotiation supports strict and non-strict behavior and copies the kernel PDU size back to userspace.

## Cross-File Relationships
- Public/stub declarations are in `bpf_filter.h`.
- Uses opcode metadata from `io_issue_defs`, including optional filter PDU populate callbacks from specific opcode implementations.
- `openclose` and `net` headers are included for opcode-specific filter context population support.

## Risks / Review Notes
- RCU/refcount ownership is subtle: freeing stops walking a filter chain when a node still has references.
- `DENY_REST` fills only currently empty opcode slots; existing filters are preserved.
- Filter instruction validation mutates some BPF load instructions before program creation.
