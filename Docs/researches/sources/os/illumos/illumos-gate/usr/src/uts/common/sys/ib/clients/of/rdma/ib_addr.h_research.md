# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/rdma/ib_addr.h

## Purpose

Defines OFED-compatible RDMA device address helpers for IPoIB/InfiniBand address data embedded in hardware address buffers.

## Main Definitions

- Imported-license comment for OFED `ib_addr.h`.
- `MAX_ADDR_LEN` set to 32 bytes.
- `struct rdma_dev_addr`: source device address, destination device address, broadcast address, and RDMA node type.
- `ip_addr_size()` returns IPv4 or IPv6 sockaddr size based on `sa_family`.
- Inline helpers to get/set P_Key from `broadcast[8..9]`.
- Inline helpers to get multicast GID from `broadcast + 4`.
- Inline helpers to get/set SGID from `src_dev_addr + 4`.
- Inline helpers to get/set DGID from `dst_dev_addr + 4`.

## Integration Notes

This header is used by OFED-compatible RDMA code that expects Linux-style device-address packing. It depends on `ib_verbs.h` for `enum rdma_node_type` and `union ib_gid`.

## Risks and Gotchas

- Offsets are protocol/ABI assumptions. The helpers blindly copy at fixed offsets inside 32-byte arrays.
- `ip_addr_size()` treats anything other than `AF_INET6` as IPv4.
