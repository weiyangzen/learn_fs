# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/api.h

## Role

Defines the kernel consumer API for the illumos Kernel Cryptographic Framework.

## Common Handles and Request State

- `crypto_req_id_t`
- `crypto_bc_t`
- `crypto_context_t`
- `crypto_ctx_template_t`
- `crypto_call_flag_t`
- Flags:
  - `CRYPTO_ALWAYS_QUEUE`
  - `CRYPTO_NOTIFY_OPDONE`
  - `CRYPTO_SKIP_REQID`
- `crypto_call_req_t`: callback, callback argument, flags, and request id.

## Mechanism and Context Templates

- `CRYPTO_MECH_INVALID`
- `crypto_mech2id()`
- `crypto_create_ctx_template()`
- `crypto_destroy_ctx_template()`

## Operation Families

The header declares single-part, init/update/final multipart, and provider-specific variants for:

- Digest.
- MAC and MAC verify.
- Sign, sign recover.
- Verify, verify recover.
- Encryption.
- Decryption.
- Encrypt/MAC dual operation.
- MAC/decrypt and MAC-verify/decrypt dual operations.

Most families include both provider-neutral and `_prov` variants that accept `crypto_provider_t` and session ids.

## Session, Object, and Key Management

Session APIs:

- `crypto_session_open()`
- `crypto_session_close()`
- `crypto_session_login()`
- `crypto_session_logout()`

Object APIs:

- copy, create, destroy, get/set attribute value, get size, find init/find/final.

Key APIs:

- derive, generate, generate pair, unwrap, wrap, key check by provider or framework.

## Async Cancellation

- `crypto_cancel_req()`
- `crypto_cancel_ctx()`

## Mechanism Lists and Provider Info

- `crypto_get_mech_list()`
- `crypto_free_mech_list()`
- `crypto_get_provider()`
- `crypto_get_provinfo()`
- `crypto_release_provider()`

## Event Notification

Events:

- `CRYPTO_EVENT_MECHS_CHANGED`
- `CRYPTO_EVENT_PROVIDER_REGISTERED`
- `CRYPTO_EVENT_PROVIDER_UNREGISTERED`

Types:

- `crypto_event_change_t`
- `crypto_notify_event_change_t`
- `crypto_notify_handle_t`
- `crypto_notify_callback_t`

APIs:

- `crypto_notify_events()`
- `crypto_unnotify_events()`

## Buffer Callback API

- `crypto_bufcall_alloc()`
- `crypto_bufcall_free()`
- `crypto_bufcall()`
- `crypto_unbufcall()`

## Mechanism Information

- Usage flags:
  - encrypt
  - decrypt
  - MAC
- `crypto_mechanism_info_t`
- 32-bit syscall variant.
- `crypto_get_all_mech_info()`
- `crypto_free_all_mech_info()`

## Research Relevance

This is the main kernel-facing crypto consumer surface. It is relevant to encrypted storage, checksums/MACs, IPsec, module verification, ZFS crypto-adjacent paths, and device/provider selection.
