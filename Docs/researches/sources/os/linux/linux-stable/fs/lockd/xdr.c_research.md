# File Research: sources/os/linux/linux-stable/fs/lockd/xdr.c

## Summary
Legacy NLM v1/v3 XDR encode/decode support for lockd server procedures.

## Main APIs
Decoders: `nlmsvc_decode_testargs()`, `nlmsvc_decode_lockargs()`, `nlmsvc_decode_cancargs()`, `nlmsvc_decode_unlockargs()`, `nlmsvc_decode_res()`, `nlmsvc_decode_reboot()`, `nlmsvc_decode_shareargs()`, `nlmsvc_decode_notify()`. Encoders: `nlmsvc_encode_testres()`, `nlmsvc_encode_res()`, `nlmsvc_encode_shareres()`, `nlmsvc_encode_void()`.

## Behavior
The old protocol decoder requires NLM file handles to be exactly `NFS2_FHSIZE`, despite protocol text allowing variable opaque handles. Lock ranges use signed 32-bit start/length values, mapped to `loff_t`; zero length or wraparound-style negative end means EOF. Test replies encode a conflicting holder only for denied locks.

## State and Data Flow
Decoded lock owner handles and caller names point into XDR stream memory. Share decoding initializes a synthetic lock with `LOCKD_SHARE_SVID`. Share replies append a zero sequence field.

## Dependencies
`svcxdr.h`, SunRPC XDR streams, NFSv2 file handle sizes, generic VFS `file_lock` initialization, and `xdr.h` structures.

## Risks
The file comments note missing range checks in original share decoding. Offset conversion clamps encoded holder ranges to `NLM_OFFSET_MAX`, so large kernel ranges can be truncated on the wire.
