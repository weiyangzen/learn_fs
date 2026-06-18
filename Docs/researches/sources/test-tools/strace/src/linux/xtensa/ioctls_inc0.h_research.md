<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/ioctls_inc0.h -->
# sources/test-tools/strace/src/linux/xtensa/ioctls_inc0.h

Purpose: Xtensa ioctl include-set shim.
Important APIs/types/functions: includes `../32/ioctls_inc.h`, reflecting Xtensa's 32-bit ABI.
Control flow: no local logic. State and persistence behavior: compile-time include only.
Dependencies and integration points: generated ioctl table production. Risks: incorrect word-size include set affects encoded ioctl sizes. Test signals: generated-table diffs and 32-bit ioctl structure-size tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/ioctls_inc0.h -->
