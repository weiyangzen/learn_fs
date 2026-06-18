# File Research: sources/os/plan9/9front/sys/src/cmd/syscall/mktab.awk

`mktab.awk` generates syscall dispatch metadata for `syscall.c`.

Behavior:
- For each input row, appends the second field as an enum name and emits a `struct Call tab[]` entry indexed by that enum.
- Entry names are lowercased strings and function symbols are also lowercased, cast to `int(*)(...)`.
- The `END` block appends special `READ`, `WRITE`, and `NTAB` enum values plus table entries for libc `read`, `write`, and the terminator `{nil, 0}`.

Output shape:
- Emits an `enum{ ... };`.
- Emits `struct Call tab[] = { ... };`.

Risks:
- Assumes the second input field is a valid enum/function token.
- Generated casts bypass type checking by design so arbitrary syscall signatures can be invoked through a uniform varargs-like call site.
