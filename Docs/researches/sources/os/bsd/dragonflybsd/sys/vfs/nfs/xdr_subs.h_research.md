# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/xdr_subs.h

This header provides NFS XDR conversion macros around `htonl` and `ntohl`. It covers unsigned 32-bit conversion, NFSv2 timestamp conversion between seconds/microseconds and `timespec`, NFSv3 timestamp conversion between seconds/nanoseconds and `timespec`, and 64-bit “hyper” conversion from/to two 32-bit network-order words.

Important macros: `fxdr_unsigned`, `txdr_unsigned`, `fxdr_nfsv2time`, `txdr_nfsv2time`, `fxdr_nfsv3time`, `txdr_nfsv3time`, `fxdr_hyper`, and `txdr_hyper`.

Research notes: the macros intentionally use 32-bit network byte-order operations even on big-endian machines and avoid relying on alignment. The NFSv2 timestamp macros treat all-ones microseconds and `tv_nsec == -1` as a special sentinel.
