# File Research: sources/virtualization/spdk/module/bdev/crypto/vbdev_crypto_rpc.c

This file implements runtime RPCs for crypto vbdev creation and deletion. `bdev_crypto_create` decodes `base_bdev_name`, `name`, and optional legacy fields `crypto_pmd`, `key`, `cipher`, `key2`, plus modern `key_name`. If `key_name` is supplied and found, it uses the existing accel key and ignores legacy crypto parameters. Without a key name, it defaults the cipher to `AES_CBC`, generates a key name from bdev name and cipher, finds or creates an accel crypto key, then creates `vbdev_crypto_opts` and calls `create_crypto_disk()`.

The create path carefully handles ownership: if this RPC created a key and later fails, it destroys the key; if the created crypto opts are accepted by the module, key destruction becomes the module's responsibility when `key_owner` is true. It also zeroes decoded key strings before freeing the generated RPC context.

`bdev_crypto_delete` decodes `name`, calls `delete_crypto_disk()`, and reports boolean success from the async unregister callback or an SPDK error response. The file is mostly glue around generated RPC contexts and the crypto vbdev management functions.
