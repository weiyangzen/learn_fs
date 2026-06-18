# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_simple.c

Read completely: 319 lines.

Implements `rpc_reg()`, the simplified server registration front end used by `registerrpc()`-style code. It creates or reuses one service transport per netid for the requested nettype, allocates a shared XDR argument buffer per netid, registers a universal dispatcher with `svc_reg()`, and records each `(program, version, procedure, netid)` in `proglst`.

The universal dispatcher handles `NULLPROC` with an empty reply, finds the matching registration for the incoming program/version/procedure/netid, zeroes the shared input buffer, decodes arguments, calls the registered function, sends the encoded reply, and frees decoded arguments.

This interface is intentionally simple but constrained: one shared argument buffer per netid limits usable argument size to the transport receive size and serialization is guarded by `proglst_lock`, so registered procedure callbacks run while that lock is held.
