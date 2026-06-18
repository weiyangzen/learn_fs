# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb2_rq.h

## Purpose

`smb2_rq.h` declares the SMB2/3 request helper API implemented by `smb2_rq.c`.

## Main Interfaces

It declares `smb2_rq_parsehdr()`, `smb2_rq_fillhdr()`, `smb2_rq_simple()`, `smb2_rq_simple_timed()`, and `smb2_rq_internal()`.

## Dependencies

The header depends on `struct smb_rq` being visible to includers through other SMB client headers. It includes `<sys/types.h>` and documents that SMB2 structures should be padded to 8-byte boundaries.

## Research Notes

This is a narrow interface header. Its main role is separating generic SMB2 request flow from operation-specific code in files such as `smb2_smb.c`.
