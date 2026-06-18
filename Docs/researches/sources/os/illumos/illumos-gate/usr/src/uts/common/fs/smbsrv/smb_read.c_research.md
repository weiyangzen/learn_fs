# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_read.c

## Purpose

`smb_read.c` implements SMB1 read command variants and common read logic for disk files and IPC named pipes. It decodes request parameters, handles lock-and-read, rejects obsolete raw read, encodes read responses, checks access/locks, and updates ofile seek position.

## Main Interfaces

- `smb_pre_read()`, `smb_post_read()`, and `smb_com_read()` implement core `SMB_COM_READ`.
- `smb_pre_lock_and_read()`, `smb_post_lock_and_read()`, and `smb_com_lock_and_read()` implement core-plus lock-and-read.
- `smb_pre_read_raw()`, `smb_post_read_raw()`, and `smb_com_read_raw()` provide an unsupported read-raw handler for tracing and proper errors.
- `smb_pre_read_andx()`, `smb_post_read_andx()`, and `smb_com_read_andx()` implement `SMB_COM_READ_ANDX`, including 64-bit offset and large-read count decoding.
- `smb_common_read()` performs the actual disk or pipe read.

## Behavior And Data Flow

Core reads decode 32-bit offsets and 16-bit counts, cap core read size at `SMB_CORE_READ_MAX`, call common read, and encode returned raw data. Lock-and-read validates a disk tree, applies a 16-bit SMB1 PID byte-range lock with no waiting, then reads only if the lock succeeds.

Read-andX decodes either 10-word or 12-word forms. The 12-word LM 0.12 form combines high and low offset fields and can combine high and low count fields when `CAP_LARGE_READX` is negotiated, ignoring `maxcnt_high == 0xFF`. Requests at or above `SMB_READX_MAX` are clamped to zero before common read. Response encoding differs for IPC versus disk: IPC uses named-pipe semantics and regular files encode `-1` in the reserved field.

`smB_common_read()` initializes a VDB/uio and routes by tree type. Disk reads reject conflicting byte-range locks, enforce execute-only access unless `SMB_FLAGS2_READ_IF_EXECUTE` is set, allocate mbufs, call `smb_fsop_read()`, trim and attach returned data. IPC reads allocate mbufs and call `smb_opipe_read()`. Both update `param->rw_count`, optional `rw_mincnt`, `rw_offset`, and `ofile->f_seek_pos`.

## Dependencies

This file depends on SMB request decoding/encoding, file lookup/release, byte-range locking, `smb_fsop_read`, named-pipe read support, mbuf allocation/trimming, tree share type macros, and ofile credentials/state.

## Notable Invariants And Risks

- All command handlers must look up and validate the FID before calling `smb_common_read()`.
- Lock-and-read uses SMB1 16-bit PID semantics.
- Directory reads skip byte-range checks but still go through filesystem read behavior.
- Execute-only handles can be read only when the request explicitly sets `SMB_FLAGS2_READ_IF_EXECUTE`.
- Named-pipe reads may block and rely on pipe cancellation/teardown behavior from `smb_opipe.c`.
- `f_seek_pos` is advisory legacy state; SMB read/write requests carry explicit offsets.
