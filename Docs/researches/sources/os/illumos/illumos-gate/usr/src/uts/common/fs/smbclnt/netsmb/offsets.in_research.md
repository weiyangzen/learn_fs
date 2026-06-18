# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/offsets.in

## Purpose

`offsets.in` is input for `ctfstabs`, used to generate `ioc_check.h` so SMB client ioctl data structures can be checked for 32-bit and 64-bit ABI layout invariance.

## Contents

The file includes kernel and SMB client headers, then lists structures and selected members whose offsets or sizes must be tracked. Covered structures include `smbioc_sockaddr`, `smbioc_ssn_ident`, `smbioc_ossn`, `smbioc_oshare`, `smbioc_tcon`, `smbioc_ssn_work`, `smbioc_rw`, `smbioc_xnp`, `smbioc_ntcreate`, `smbioc_printjob`, and `smbioc_pk`.

Several entries request generated size or field constants such as `SIZEOF_SMBIOC_RW`, `SIZEOF_SMBIOC_XNP`, `SIZEOF_NTCREATE`, `IOC_NTCR_NAME`, `SIZEOF_PRINTJOB`, and `SIZEOF_SMBIOC_PK`.

## Dependencies

The generated output depends on definitions from `<netsmb/smb.h>`, `<netsmb/netbios.h>`, `<netsmb/smb_dev.h>`, and system type/DDI/socket headers.

## Research Notes

This file is ABI guard metadata, not runtime logic. Changes to SMB ioctl structures should update or validate this list so 32/64-bit ioctl compatibility remains checked.
