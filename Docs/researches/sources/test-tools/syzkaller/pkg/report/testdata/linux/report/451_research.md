# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/451

Purpose: golden fixture for an intentional LKDTM-style bad address dereference. Expected title is `general protection fault in deliberately_dereference_bad_address`, alternate title is `bad-access in deliberately_dereference_bad_address`, and type is `DoS`.

Important APIs, types, and functions: parser fields cover GPF recognition and bad-access alternate-title creation. Kernel frames include `deliberately_dereference_bad_address`, `do_vfs_ioctl`, `ksys_ioctl`, `__x64_sys_ioctl`, `do_syscall_64`, and syscall entry.

Control flow: an ioctl process triggers a non-canonical address GPF with KASAN `maybe wild-memory-access` output. The parser must title from the kernel RIP, preserve syscall-origin context as supporting evidence, and not require a panic tail.

State and persistence behavior: static non-panicking crash fixture. Persisted state is limited to the expectation headers and the raw GPF report.

Dependencies and integration points: depends on x86 GPF parsing, KASAN auxiliary-line tolerance, and alternate-title mapping for bad accesses. It integrates ioctl-triggered LKDTM fault injection into report tests.

Risks: helper frames and repeated final RIP/register blocks can cause duplicated extraction. The magic address `00badbeefbadbeef` should be evidence, not part of title normalization.

Test signals: `general protection fault for non-canonical address`, KASAN wild-memory-access range, `RIP: deliberately_dereference_bad_address+0x33/0x60`, and ioctl syscall frames.
