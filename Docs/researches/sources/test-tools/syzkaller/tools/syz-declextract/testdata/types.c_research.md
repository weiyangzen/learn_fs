# sources/test-tools/syzkaller/tools/syz-declextract/testdata/types.c

Purpose: this fixture stresses type extraction: anonymous structs/unions, typedefs, forward pointers, bitfields, packed/aligned attributes, recursive structs, enum typedefs, user pointers, counted-by attributes, zero-length arrays, and alignment edge cases.

Important APIs and flow: it defines `anon_t`, `empty_struct`, `fd_t`, `forward_t`, `struct anon_struct` with nested anonymous members, arrays, pointers, and pointer arrays; bitfield enum and `struct bitfields` with unnamed bitfield and counted pointer; packed/aligned structs; mutually recursive `various` and `recursive`; syscalls `types_syscall`, `types_syscall2`, and `align_syscall`; `anon_flow` assigns one input into nested fields; and several alignment test structs.

State and persistence: no persistence. Struct fields and local assignments exist to test extracted field facts and layout.

Dependencies and integration: includes fixture `types.h` and `syscall.h`. Paired JSON feeds struct layout, enum, syscall, and field-flow checks in declextract tests.

Risks: generated anonymous struct names are synthetic and can be unstable if naming algorithms change. Layout expectations depend on the compiler target ABI.

Test signals: paired JSON lists many structs with size/alignment, enum constants, syscall arg types, user-pointer annotations, counted-by metadata, and `anon_flow` field facts.
