# sources/test-tools/syzkaller/tools/syz-declextract/testdata/include/types.h

Purpose: this fixture header supplies kernel-style integer aliases, `__user` pointer annotation, `ARRAY_SIZE`, and atomic helper functions for declextract tests.

Important APIs and flow: typedefs define `s8/s16/s32/s64` and `u8/u16/u32/u64`. `__user` expands to a BTF type tag attribute. `ARRAY_SIZE` computes element count. `atomic_load32` and `atomic_load64` wrap `__atomic_load_n` and appear in JSON function outputs.

State and persistence: no state beyond static inline function bodies.

Dependencies and integration: included by `functions.c`, `netlink.h`, and `types.c`, and indirectly by netlink fixtures. It supports type extraction and user-pointer recognition.

Risks: compiler-specific attributes and builtins are simplified. The atomic helpers are present for extraction visibility, not for runtime execution.

Test signals: golden JSON confirms fixed-width aliases, user pointer handling, inline/static function extraction, and array-size macro use.
