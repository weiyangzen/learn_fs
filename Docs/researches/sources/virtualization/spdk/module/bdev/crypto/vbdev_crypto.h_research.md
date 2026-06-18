# File Research: sources/virtualization/spdk/module/bdev/crypto/vbdev_crypto.h

This header defines the crypto vbdev management interface and option structure. `BDEV_CRYPTO_DEFAULT_CIPHER` is `"AES_CBC"` for legacy QAT/AESNI_MB-style configuration, although the implementation also supports key-name based accel keys.

`struct vbdev_crypto_opts` stores virtual bdev name, base bdev name, `spdk_accel_crypto_key *`, and whether the key is owned by the vbdev/RPC path and must be destroyed when the association is removed. The header declares creation, deletion, option allocation by name, and option cleanup functions. It includes SPDK RPC/util/string/log/accel/bdev headers because the RPC and implementation share these declarations.
