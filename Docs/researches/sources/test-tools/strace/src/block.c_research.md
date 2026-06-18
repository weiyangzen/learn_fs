# sources/test-tools/strace/src/block.c

Purpose: multipers-aware ioctl decoder for block-device ioctl commands.

Important APIs/types/functions: `MPERS_PRINTER_DECL(int, block_ioctl, ...)`, type aliases for `struct_blk_user_trace_setup`, `struct_blkpg_ioctl_arg`, `struct_blkpg_partition`, `print_blkpg_req`, `umove_or_printaddr`, numeric printers, pair printers, xlat `blkpg_ops`, and many `BLK*` ioctl constants.

Control flow: switch on ioctl `code`. Some commands treat `arg` as an immediate value, some decode output values only on exit, some decode input integers or integer pairs immediately, `BLKPG` reads nested partition data and prints a struct, and `BLKTRACESETUP` prints most fields on entry then appends the kernel-filled name on successful exit. Unknown commands return plain `RVAL_DECODED` for fallback handling; recognized commands return `RVAL_IOCTL_DECODED`.

State and persistence behavior: no persistent state. Reads tracee memory for ioctl argument structures and output values. Entry/exit handling for `BLKTRACESETUP` relies on strace syscall phase state.

Dependencies and integration points: part of the ioctl decoder dispatch; uses mpers type generation so structure layout matches tracee ABI, and build rules in `Makefile.am` generate printer tables for native/m32/mx32 variants.

Risks: ioctl constants and struct layouts are kernel-version and ABI sensitive. Entry-only and exit-only commands must match kernel direction semantics or output can be misleading. Nested `blkpg->data` pointer decoding can fail independently from the outer struct.

Test signals: ioctl tests for block devices should cover immediate values, integer outputs, `BLKGETSIZE64`, discard pairs, `BLKPG`, `BLKTRACESETUP` success/failure, and unknown block ioctls.
