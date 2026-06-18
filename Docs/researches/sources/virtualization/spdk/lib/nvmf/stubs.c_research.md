# File Research: sources/virtualization/spdk/lib/nvmf/stubs.c

## Purpose

`stubs.c` provides fallback implementations for optional NVMe-oF features when SPDK is built without selected configuration capabilities. It keeps the NVMf library linkable while making unsupported feature use explicit.

## Conditional Stub Areas

### Authentication Without EVP MAC

When `SPDK_CONFIG_HAVE_EVP_MAC` is not defined, this file stubs NVMe-oF authentication support:

- `nvmf_qpair_auth_init()` returns `-ENOTSUP`.
- `nvmf_qpair_auth_destroy()` asserts that `qpair->auth` is `NULL`.
- `nvmf_qpair_auth_dump()` emits nothing.
- `nvmf_auth_request_exec()` completes the request with generic invalid opcode status and returns asynchronous completion status.
- `nvmf_auth_is_supported()` returns `false`.
- Registers the `nvmf_auth` log component in this build mode.

The behavior is explicit: authentication is unavailable, and authentication commands are rejected as invalid opcodes.

### RDMA Hooks Without RDMA

When `SPDK_CONFIG_RDMA` is not defined, `spdk_nvmf_rdma_init_hooks()` logs an error and aborts. This prevents code from silently installing RDMA hooks in a build that lacks RDMA transport support.

### mDNS PRR Without Avahi

When `SPDK_CONFIG_AVAHI` is not defined, this file stubs mDNS PRR publishing:

- `nvmf_publish_mdns_prr()` logs that Avahi support is required and returns `-ENOTSUP`.
- `nvmf_tgt_stop_mdns_prr()` is a no-op.
- `nvmf_tgt_update_mdns_prr()` returns success.

## Dependencies

The file includes SPDK config, logging, NVMe-oF transport declarations, and `nvmf_internal.h`. Its behavior is entirely controlled by compile-time feature macros.

## Role in the Source Tree

This is a small build-configuration compatibility file. It does not implement normal transport or filesystem behavior; instead, it defines clear failure/no-op behavior for optional authentication, RDMA, and Avahi-dependent mDNS features when those dependencies are absent.
