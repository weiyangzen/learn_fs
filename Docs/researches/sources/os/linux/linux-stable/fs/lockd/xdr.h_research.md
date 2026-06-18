# File Research: sources/os/linux/linux-stable/fs/lockd/xdr.h

## Summary
Shared legacy NLM XDR data types and function prototypes.

## Contents
Defines statd constants, cookie/string limits, NLM status `__be32` constants, `struct nlm_lock`, `struct nlm_cookie`, `struct nlm_args`, `struct nlm_res`, and `struct nlm_reboot`.

## Behavior
`struct nlm_lock` carries both wire-level fields and the in-kernel `struct file_lock`. Cookies are fixed at 32 bytes for Linux interoperability with common clients. `nlm_args` is the common request container for lock, share, notify, and state fields.

## Dependencies
Linux file locks, NFS file handles, and SunRPC XDR.

## Risks
This header is shared by server procedure and XDR code, so field ownership is mixed: some pointers alias XDR buffers, while `file_lock` private state needs explicit release.
