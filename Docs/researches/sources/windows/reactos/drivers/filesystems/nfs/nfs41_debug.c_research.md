# File Research: sources/windows/reactos/drivers/filesystems/nfs/nfs41_debug.c

This file implements debug and trace helpers for the ReactOS/Windows NFSv4.1 mini-redirector.

Core printing:
- `DbgP` and `print_error` format messages into fixed 512-byte buffers using `RtlStringCbVPrintfA` and emit via `DbgPrintEx`.
- Optional timestamp code is present behind `INCLUDE_TIMESTAMPS`.
- `dprintk` provides a Toaster-style formatted trace helper with a 1024-byte buffer and explicit debug flags.

Data dump helpers:
- `print_hexbuf` dumps buffers in hex.
- `print_basic_info`, `print_std_info`, `print_ea_info`, and `print_get_ea` print common file information structures.
- `print_file_object`, `print_fo_all`, `print_srv_call`, `print_net_root`, `print_v_net_root`, `print_fcb`, `print_srv_open`, and `print_fobx` print selected RDBSS object state, with many deeper fields compiled out under `#if 0`.

Operation decoders:
- `print_ioctl` decodes major device/filesystem/internal-control IRP categories.
- `print_fs_ioctl` decodes NFS driver IOCTLs such as invalidate cache, read/upcall, write/downcall, add/delete connection, get state, start, and stop.
- `print_driver_state` maps driver state constants to names.
- `print_file_information_class` and `print_fs_information_class` convert information-class IDs to strings.
- `opcode2string` maps NFS upcall/downcall opcodes such as mount, open, read, write, lock, directory query, ACL query, and ACL set.

Request diagnostics:
- `print_irp_flags`, `print_irps_flags`, and `print_nt_create_params` expand flags, create disposition/options, share access, desired access, and file attributes.
- `print_caching_level` decodes cache policy flags.
- `print_acl_args` prints selected security-information bits.
- `print_open_error` maps common open failure statuses to readable labels.
- `print_wait_status` explains wait results and optionally includes opcode, entry pointer, and transaction ID.

Research notes:
- This file has no core NFS protocol implementation; it is diagnostic support.
- Most helpers are gated by an `on` parameter, so callers can cheaply disable verbose output.
- The file bridges ReactOS compatibility by declaring UTF-8 conversion routines for older NTDDI targets.
