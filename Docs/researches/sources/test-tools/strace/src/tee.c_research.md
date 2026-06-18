# sources/test-tools/strace/src/tee.c

Purpose: ioctl decoder for Linux TEE devices.

Important APIs/types/functions: `tee_ioctl`, `tee_fetch_buf_data`, `tee_print_param_fn`, `tee_print_params`, and decoders for `TEE_IOC_VERSION`, `OPEN_SESSION`, `INVOKE`, `CANCEL`, `CLOSE_SESSION`, `SUPPL_RECV`, `SUPPL_SEND`, `SHM_ALLOC`, `SHM_REGISTER_FD`, and `SHM_REGISTER`. Uses TEE xlat tables for implementation IDs, capabilities, login types, origins, parameter attributes, and shared-memory flags.

Control flow: dispatches by ioctl code. Buffer-based calls first fetch `tee_ioctl_buf_data`, validate `buf_len` against fixed header size and `TEE_MAX_ARG_SIZE`, fetch the pointed argument header, validate parameter array size on entry, and print parameter arrays. Many ioctls print input fields on entry and changed output fields on exit using nested structs and `tprint_value_changed`.

State and persistence behavior: stateless decoder; reads tracee structures and parameter arrays, no persistent cache.

Dependencies and integration points: called from the generic ioctl decoder for TEE device commands; depends on `<linux/tee.h>` and generic tracee memory fetch/array printers.

Risks: `buf_len`, `num_params`, and `buf_ptr` validation protects against decoding buffers the kernel will reject. Pointer arithmetic uses fixed kernel ABI layouts; malformed tracee memory should fall back to printing the buffer descriptor.

Test signals: version for OP-TEE and unknown implementations, open/invoke success/failure, group login GID interpretation, every param attr family, supplier recv/send output updates, shared memory allocation/register, invalid `buf_len`, bad `buf_ptr`, and zero params.
