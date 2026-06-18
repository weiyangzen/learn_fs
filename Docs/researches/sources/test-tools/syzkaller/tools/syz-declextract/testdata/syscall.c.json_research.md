# sources/test-tools/syzkaller/tools/syz-declextract/testdata/syscall.c.json

Purpose: this golden JSON describes basic syscall extraction for `syscall.c`.

Important structure: top-level keys are `functions` and `syscalls`. Functions are `__do_sys_chmod` and `__do_sys_open`. Syscall records include typed arguments: const string buffer pointer for `filename` and 4-byte integer fields for `flags` and `mode`.

State and persistence: static cache input for the declextract tests.

Dependencies and integration: consumed through `TestDeclextract` to generate and compile descriptions.

Risks and test signals: focused signal for syscall arg typing; it does not cover syscall renaming or arch table lookup.
