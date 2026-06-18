# File Research: sources/virtualization/spdk/lib/keyring/keyring_internal.h

Provides the private keyring header shared by the keyring implementation and keyring RPC code.

Key contents:
- Includes `spdk/json.h` and `spdk/keyring.h`.
- Declares `keyring_dump_key_info(struct spdk_key *key, struct spdk_json_write_ctx *w)`.
- Uses a normal include guard, `SPDK_KEYRING_INTERNAL_H`.

Filesystem/block relevance:
- This header keeps the RPC layer from duplicating key metadata serialization logic while leaving the helper out of the public keyring API.
