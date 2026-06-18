# sources/test-tools/strace/src/process_vm.c

Purpose: Decodes `process_vm_readv` and `process_vm_writev` syscall arguments.

Important APIs/types/functions: `SYS_FUNC(process_vm_readv)` and `SYS_FUNC(process_vm_writev)`.

Control flow: readv prints pid on entry, then on exit prints local iovecs as strings up to return value when successful or addresses on error, remote iovecs as addresses, counts, and flags. writev prints all arguments on entry and returns decoded.

State and persistence: no persistent state; relies on `tcp->u_rval` on read exit to bound local data rendering.

Dependencies/integration: uses `tprint_iov`, `tprint_iov_upto`, `iov_decode_str`, `iov_decode_addr`, and pid helpers.

Risks: successful read output depends on correct return-value clipping; decoding huge iovec counts must be bounded by common iovec helpers. Flags are currently numeric because the syscall defines no meaningful flags.

Test signals: read/write success and failure, partial reads, multiple iovecs, invalid iovec pointers, and nonzero flags.
