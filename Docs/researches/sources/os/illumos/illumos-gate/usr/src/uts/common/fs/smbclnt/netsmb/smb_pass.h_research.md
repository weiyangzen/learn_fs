# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_pass.h

## Purpose
Declares the SMB password-hash keychain data structure and lifecycle functions used by the nsmb driver.

## Key Elements
Defines `smb_passid_t`, the AVL-tree node containing UID, zone ID, server/domain string, username string, and fixed-size LM/NT hash buffers. The comment notes the structure is exposed here mainly so the mdb module can inspect it; otherwise it could be private to `smb_pass.c`.

Declares `smb_pkey_init`, `smb_pkey_fini`, and `smb_pkey_idle`, which are called from driver initialization, finalization, and unload-idle checks.

## Dependencies
Includes illumos AVL definitions and SMB ioctl constants/hash sizes from `smb_dev.h`.

## Behavior/Risks
Because this header exposes credential-cache internals for debugging, structure layout changes can affect mdb/debug tooling as well as the implementation. The stored hash buffers are sensitive and require teardown paths to keep freeing nodes consistently.
