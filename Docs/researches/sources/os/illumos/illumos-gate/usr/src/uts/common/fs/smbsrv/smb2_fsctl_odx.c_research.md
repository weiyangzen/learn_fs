# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_fsctl_odx.c

Read completely. This file implements SMB2/FSCTL offloaded data transfer: `FSCTL_OFFLOAD_READ` and `FSCTL_OFFLOAD_WRITE`.

ODX read returns a 512-byte storage offload token representing a source range. The implementation supports a standard zero-data token and a server-native token carrying source SMB2 file ID, source offset, source EOF, and source tree ID. Tunables include `smb2_odx_enable`, `smb2_odx_read_max`, `smb2_odx_write_max`, and `smb2_odx_buf_size`.

`smb2_fsctl_odx_read()` validates read access, input/output sizes, block alignment, regular non-stream file constraints, delete state, locks, and EOF. It uses `smb_fsop_next_alloc_range()` to decide whether the requested range is entirely a hole. Hole ranges receive a zero-data token; data ranges receive a native token. It can set the all-zero-beyond flag when no more data exists.

`smb2_fsctl_odx_write()` validates write access, decodes write arguments and token, checks output size, block alignment, destination type, delete state, locks, and EOF. Zero tokens are handled by `smb2_fsctl_odx_write_zeros()`, which punches holes and extends the file when needed. Native tokens are handled by `smb2_fsctl_odx_write_native1()`, which locates the source ofile, possibly through another tree, validates source access, allocates a copy buffer, and uses `smb2_sparse_copy()`.

Token wire helpers `smb_odx_get_token()` and `smb_odx_put_token()` handle fixed 512-byte token framing and big-endian token metadata. EOF crossing and block-aligned transfer reporting are carefully handled so clients can continue copy loops correctly.
