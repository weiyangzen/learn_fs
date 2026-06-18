# File Research: sources/virtualization/spdk/lib/util/Makefile

This Makefile builds SPDK’s general-purpose `util` library.

It compiles utility sources including base64, bit arrays, cpuset, CRCs, DIF, fd groups, file helpers, hex/iov/math/net/pipe/string/uuid/xor/zipf/md5, sets shared-library version `SO_VER := 12` and `SO_MINOR := 0`, conditionally links `libuuid`, OpenSSL, and ISA-L, adds `-Wpointer-arith`, uses `spdk_util.map`, and includes standard SPDK build rules.

The listed files in this group are only a subset of the utility library’s source list.
