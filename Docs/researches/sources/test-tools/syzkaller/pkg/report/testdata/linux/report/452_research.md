# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/452

Purpose: companion golden fixture for a segment-related general protection fault in `deliberately_dereference_bad_address`. Expected title and alternate match report `451`, with type `DoS`.

Important APIs, types, and functions: parser coverage is GPF detection, title normalization across related fault wording, and bad-access alternate generation. Kernel frames include `deliberately_dereference_bad_address`, `do_vfs_ioctl`, `ksys_ioctl`, `__x64_sys_ioctl`, and `do_syscall_64`.

Control flow: the log starts with `segment-related general protection fault: beec`, reports RIP at offset `+0x1b`, shows ioctl call trace, and then repeats an older RIP/register block at offset `+0x33`. The parser must use the active fault site but normalize to the same function-level title.

State and persistence behavior: static fixture with no panic and no `REPORT:` block. It persists variant GPF wording and repeated RIP text.

Dependencies and integration points: depends on Linux x86 GPF regexes and title canonicalization by function name. It integrates fault-injection ioctl behavior with report deduplication across similar bad-address crashes.

Risks: repeated trailing RIP from another fault context may confuse start/end handling. Segment-related wording must still map to a general protection fault.

Test signals: `segment-related general protection fault: beec`, first `RIP: deliberately_dereference_bad_address+0x1b/0x60`, ioctl stack, and repeated `badbeef` register state.
