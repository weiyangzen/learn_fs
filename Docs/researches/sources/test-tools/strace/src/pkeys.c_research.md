<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/pkeys.c -->
# sources/test-tools/strace/src/pkeys.c

Purpose: decodes memory protection key allocation and free syscalls.

Important APIs/types/functions: `SYS_FUNC(pkey_alloc)`, `SYS_FUNC(pkey_free)`, and `pkey_access` xlat.

Control flow: `pkey_alloc` prints raw flags and symbolic access rights; `pkey_free` prints the signed key id.

State and persistence behavior: no decoder state.

Dependencies and integration points: syscall table integration and generated protection-key access xlat.

Risks: allocation flags are printed raw because no symbolic table is used here. Access-right additions need xlat updates.

Test signals: pkey allocation with disable-access/disable-write combinations, unknown access bits, and freeing valid/invalid pkeys.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/pkeys.c -->
