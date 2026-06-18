# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_xdr.c

## Purpose

`nfs4_xdr.c` is the hand-written illumos NFSv4 XDR implementation for the kernel NFS client and server. It serializes and deserializes NFSv4 compound arguments/results, filehandles, bitmaps, attributes, stateids, lock/open payloads, READ/WRITE data, READDIR streams, callback compounds, and selected NFSv4.1 extension operations through `nfs4x_xdr.c` hooks.

The file is performance-sensitive protocol plumbing. It uses inline XDR fast paths, direct decode into kernel objects such as `vattr_t` and `dirent64_t`, RDMA chunk registration/validation, mblk stream support, and custom memory-free paths for compound arrays.

## Main Interfaces

Public or externally used routines include:

- Core types: `xdr_bitmap4`, `xdr_utf8string`, `xdr_nfs_fsl_info`, `xdr_knetconfig`, `xdr_nfs_fh4`, `xdr_inline_decode_nfs_fh4`, `xdr_inline_encode_nfs_fh4`
- Attribute types: `xdr_nfsace4`, `xdr_fattr4_fsid`, `xdr_fattr4_acl`, `xdr_fattr4_fs_locations`, `xdr_fattr4_rawdev`, `xdr_nfstime4`, `xdr_fattr4_sec_label`, `xdr_fattr4`, `xdr_settime4`
- Client decode helpers: `xdr_get_bitmap4_inline`, `xdr_READDIR4res_clnt`, `nfs4_init_dot_entries`, `nfs4_destroy_dot_entries`
- Server result helpers: `xdr_READDIR4res`, `xdr_SECINFO4res`
- Compound wrappers: `xdr_COMPOUND4args_clnt`, `xdr_COMPOUND4args_srv`, `xdr_COMPOUND4res_clnt`, `xdr_COMPOUND4res_srv`
- Callback wrappers: `xdr_CB_COMPOUND4args_clnt`, `xdr_CB_COMPOUND4args_srv`, `xdr_CB_COMPOUND4res`

Important private helpers include filehandle encode/decode routines, `xdr_ga_fattr_res`, `xdr_ga_fattr_res_inline`, `xdr_ga_res`, per-operation argument/result XDR routines, `xdr_nfs_argop4`, `xdr_nfs_resop4`, client/server variants for argop/resop processing, and optimized compound-array free functions.

## Filehandle And Bitmap Handling

`xdr_bitmap4()` stores the common NFSv4 bitmap as a local `uint64_t`, while preserving support for NFSv4.1 bit 75 (`FATTR4_SUPPATTR_EXCLCREAT`) by folding it into a local high bit. It always emits two words unless the folded third word is needed, and on decode it consumes and skips extra words so the XDR stream stays synchronized.

Filehandle handling has distinct client and server semantics:

- Client decode through `xdr_nfs_fh4()` treats filehandles as opaque byte arrays.
- Server-side `xdr_decode_nfs_fh4()` and `xdr_encode_nfs_fh4()` understand illumos internal `nfs_fh4_fmt_t` layout.
- Inline decode validates total filehandle size, fid/export lengths, required padding, flags, and absence of trailing bytes.
- Malformed handles are consumed from the stream but returned with zero length so upper NFS layers can reject them cleanly.

## Attribute Decode Model

The main GETATTR decode path is `xdr_ga_res()`, which reads the returned bitmap and attribute-list length, validates server response bitmaps against the requested bitmap, and then decodes attributes through either `xdr_ga_fattr_res()` or the inline fast path `xdr_ga_fattr_res_inline()`.

Decoded data lands primarily in `nfs4_ga_res_t`:

- `vattr_t` fields for file type, mode, uid/gid, size, link count, node id, rdev, times, and block count.
- Extended result data for fsid, filesystem statistics, pathconf-style properties, max read/write sizes, ACL support, lease time, fs locations, filehandle attributes, and mounted-on file id.
- `vsecattr_t` ACL data when `FATTR4_ACL_MASK` is present.

Owner and group string-to-id conversion uses `nfs_idmap_str_uid()` and `nfs_idmap_str_gid()`. A small `ug_cache_t` can cache repeated owner/group names during READDIR attribute decode, reducing repeated idmap work for directories with many entries owned by the same principals.

The code records attribute conversion failures in `n4g_attrerr` and `n4g_attrwhy` rather than necessarily failing raw XDR decode. This distinction lets callers know whether the network stream was valid but local attribute interpretation failed.

## READ, WRITE, RDMA, And mblk Paths

`xdr_READ4args()` encodes stateid, offset, count, and registers RDMA write chunks when the transport supports RDMA. It can describe either a target address buffer or caller-provided `uio`.

`xdr_READ4res()` is server-side encode-only. It supports ordinary byte payloads, prebuilt `mblk_t` payloads, `xdrmblk_ops`, and RDMA write-list data transfer through `xdrrdma_send_read_data()`.

`xdr_READ4res_clnt()` is the client decode path. It handles direct I/O into `uio`, inline memory decode, mblk streams, RDMA write-list length validation, and caller-provided alternate buffers. It rejects payloads larger than the caller-advertised maximum and verifies RDMA transferred length against the opaque count.

`xdr_WRITE4args()` decodes client write requests into ordinary buffers, mblk chains, or RDMA read chunks via `xdrrdma_getrdmablk()` and `xdrrdma_read_from_client()`. Its free path releases RDMA clists. `xdr_WRITE4res()` serializes status, written count, stable mode, and write verifier.

## Directory Handling

`nfs4_init_dot_entries()` prebuilds padded `.` and `..` `dirent64` records. `xdr_READDIR4res_clnt()` uses those records when decoding cookies 0 and 1, then decodes server entries into an `rddir4_cache` buffer.

The READDIR client decode loop:

- Reads cookie, name, attribute bitmap, attribute length, and attributes for each entry.
- Computes `DIRENT64_RECLEN()` before copying names to prevent output-buffer overflow.
- If the caller buffer fills, skips remaining names/attributes while keeping the stream synchronized.
- Sets `d_ino` from mounted-on fileid when available, otherwise from fileid.
- Optionally constructs NFSv4 rnodes and updates DNLC when both attributes and filehandle attributes are present.
- Distinguishes normal EOF, no entries, bad cookies, and too-small buffers through `rdc->error`.

Server-side `xdr_READDIR4res()` emits pre-encoded mblk data and temporarily disables RDMA chunking when needed so the encoded directory block is transferred as intended.

## Compound Operation Processing

The file implements custom NFSv4 compound serialization rather than relying on rpcgen output.

Client argument encoding is optimized by private pseudo-ops such as `OP_CPUTFH`, `OP_CLOOKUP`, `OP_COPEN`, `OP_CREMOVE`, `OP_CCREATE`, `OP_CLINK`, `OP_CRENAME`, and `OP_CSECINFO`. These avoid temporary allocations and encode C strings or shared filehandles directly into the stream.

Server argument decode uses `xdr_snfs_argop4()`, including special server decode for `OP_PUTFH` so internal filehandles are validated. Operations with opcodes at or above `OP_BACKCHANNEL_CTL` are delegated to `xdr_nfs4x_argop4()` in the NFSv4.1 XDR file.

Result handling has three variants:

- `xdr_nfs_resop4()` for generic result encoding/decoding.
- `xdr_snfs_resop4()` for server result encoding, including internal filehandle encode for `OP_GETFH` and NFSv4.1 delegation.
- `xdr_nfs_resop4_clnt()` for client result decode using the matching argop, enabling specialized GETATTR, READ, and READDIR decoding.

`xdr_COMPOUND4res_clnt()` validates response operation count against the request. A successful compound must return exactly the requested operation count; an error compound may return a shorter prefix. It tracks `decode_len` so partially decoded arrays can be safely freed after decode failure.

## Callback Processing

The callback compound routines handle the role reversal between NFS server and NFS client:

- Server-initiated callback arguments use `xdr_snfs_cb_argop4()` and encode internal server filehandles for `CB_GETATTR` and `CB_RECALL`.
- Client-side callback decode uses `xdr_cnfs_cb_argop4()` and treats callback filehandles as opaque.
- Unknown or NFSv4.1 callback operations are delegated to common callback XDR helpers so the server/client can return protocol errors rather than failing XDR prematurely.

## Memory Management And Safety

The file contains many XDR_FREE fast paths to release only fields that can allocate memory: UTF-8 strings, filehandles, ACL arrays, fs locations, SECINFO lists, READLINK strings, denied lock owners, OPEN owners/claims, WRITE buffers, and compound arrays.

Notable defensive properties:

- Bounds are applied to filehandles, UTF-8 strings, ACLs, opaque security labels, READ/WRITE data, and compound operation counts.
- Filehandle decode consumes malformed handles without desynchronizing the stream.
- GETATTR rejects unknown extra response attributes because they cannot be skipped safely without semantic knowledge.
- READDIR continues decoding skipped entries after local buffer exhaustion.
- RDMA read/write counts are validated against protocol counts.
- Free paths tolerate partially decoded arrays and invalid op placeholders.

## Dependencies

This file depends on:

- Core RPC/XDR, RDMA XDR, and mblk XDR support.
- NFSv4 protocol definitions in `nfs4_kprot.h` and related headers.
- NFSv4 client structures such as `mntinfo4_t`, `rnode4_t`, `rddir4_cache`, shared filehandles, and DNLC helpers.
- Attribute conversion helpers in NFSv4 attribute/id mapping code.
- NFSv4.1 operation XDR hooks in `nfs4x_xdr.c`.

## Research Notes

This is a trust-boundary file: untrusted network bytes become kernel filehandles, attributes, directory entries, stateids, locks, and data buffers. The highest-risk areas are inline attribute decoding, READDIR buffer accounting, server internal filehandle validation, compound partial-free behavior, RDMA length checks, and owner/group string mapping interactions with cacheability.
