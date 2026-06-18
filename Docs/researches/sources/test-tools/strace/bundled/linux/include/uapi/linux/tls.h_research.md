# sources/test-tools/strace/bundled/linux/include/uapi/linux/tls.h

## Purpose

Defines Linux kernel TLS socket option ABI for configuring record-layer crypto on TCP sockets and reporting TLS offload state. strace uses it to decode `SOL_TLS` option payloads and TLS info netlink attributes.

## Important APIs, Types, and Dependencies

The header depends on `linux/types.h`. It exports options `TLS_TX`, `TLS_RX`, `TLS_TX_ZEROCOPY_RO`, `TLS_RX_EXPECT_NO_PAD`, and `TLS_TX_MAX_PAYLOAD_LEN`; version macros for TLS 1.2 and 1.3; cipher ids and key/iv/salt/tag/record-sequence sizes for AES-GCM-128/256, AES-CCM-128, CHACHA20-POLY1305, SM4-GCM/CCM, and ARIA-GCM-128/256; record type controls; base `struct tls_crypto_info`; cipher-specific TLS 1.2 crypto info structs; `TLS_INFO_*` attributes; and config states `TLS_CONF_BASE`, `SW`, `HW`, and `HW_RECORD`.

## Control Flow, State, and Integration

Runtime flow is setting transmit or receive crypto info through socket options, enabling hardware/software TLS offload state, and querying info attributes. Persistent state is per-socket crypto material, record sequence numbers, offload mode, zero-copy receive/tx hints, and maximum plaintext length.

## Risks and Test Signals

Risks include exposing key material in traces, choosing the wrong cipher-specific struct by `cipher_type`, TLS 1.3 using the same crypto-info families with different protocol semantics, and fixed array sizes drifting with new ciphers. Test signals include option decode by cipher id, version display, redaction policy checks, and `TLS_INFO_*` netlink attributes.
