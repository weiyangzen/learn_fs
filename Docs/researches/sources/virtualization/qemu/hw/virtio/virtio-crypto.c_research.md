# File Research: sources/virtualization/qemu/hw/virtio/virtio-crypto.c

## Purpose
Implements the virtio-crypto device model backed by QEMU `cryptodev` backends, with control queue session management, data queue crypto operations, optional vhost-crypto acceleration, config reporting, and unmigratable VMState.

## Key Elements
- Session management: `virtio_crypto_handle_ctrl()` parses control queue requests, supports symmetric cipher/chaining session creation, RSA akcipher session creation, and destroy-session requests.
- Session helpers allocate and validate cipher keys, auth keys, and asymmetric keys against backend-advertised limits before calling `cryptodev_backend_create_session()` or close-session APIs.
- Completion callbacks `virtio_crypto_create_session_completion()` and `virtio_crypto_destroy_session_completion()` write virtio status/session IDs back to guest buffers and notify the queue.
- Data request parsing: `virtio_crypto_handle_request()` copies in/out iovecs, validates headers, locates the trailing input header, parses opcodes, and builds `CryptoDevBackendOpInfo`.
- Symmetric operations: `virtio_crypto_sym_op_helper()` validates lengths, bounds total data by `max_size`, lays out IV/AAD/src/dst/digest buffers in one allocation, and captures guest input data.
- Asymmetric operations: `virtio_crypto_handle_asym_req()` handles akcipher src/dst buffers and verify-specific destination input.
- Completion: `virtio_crypto_req_complete()` copies result data/digest or akcipher output into guest iovecs, writes status, pushes the used element, and frees request state.
- Queue scheduling: data queues run through guarded BHs that disable notification while draining and re-enable it after the queue becomes empty.
- Realize/unrealize: validates an unused `cryptodev`, sets `max_queues`, creates data queues plus a control queue, initializes backend-derived config fields, marks the backend used, and clears it on unrealize.
- Vhost path: `virtio_crypto_set_status()` starts/stops vhost crypto when the guest is ready, hardware is ready, and the VM is running; notifier mask/pending callbacks forward to cryptodev-vhost helpers.
- Config path reports status, queue count, service bitmaps, algorithm bitmaps, key limits, and max request size as little-endian virtio 1.0 config.

## Dependencies
Uses virtio core, iovec helpers, guarded BHs, `cryptodev` backend APIs, `cryptodev-vhost`, Linux virtio crypto headers via `virtio-crypto.h`, QOM properties, and QAPI errors.

## Behavior/Risks
- VMState is marked unmigratable.
- Only cipher, algorithm chaining, and RSA akcipher paths are implemented; hash, MAC, AEAD, DSA, and ECDSA paths are unsupported or TODO.
- Serious parse/buffer errors detach the virtqueue element and can require device reset.
- Request buffers containing key/data material are zeroized for symmetric operation info before free, but asymmetric source/destination buffers are simply freed.
- Backend ownership is exclusive; realization fails if the cryptodev backend is already used.
- Vhost start failures fall back to userspace virtio crypto.
