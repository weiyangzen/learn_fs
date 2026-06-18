# File Research: sources/virtualization/qemu/block/crypto.c

Implements QEMU's LUKS block format driver on top of `QCryptoBlock`. `BlockCrypto` stores the crypto object, an `updating_keys` permission state, and optional detached header child.

The driver provides crypto header read/write callbacks that work both in coroutine and non-coroutine contexts and choose the detached header child when present. Creation helpers support normal and detached-header LUKS creation, payload formatting, preallocation/truncate handling, legacy create-opts parsing, and `blockdev-create` QAPI options. Option conversion functions parse open/create/amend QDicts through QAPI visitors.

Open flow creates `file` and optional `header` children, parses runtime options, sets detached/no-I/O crypto flags, opens the `QCryptoBlock`, and marks the BDS encrypted. I/O paths use a 1 MiB aligned bounce buffer so guest qiovs never expose ciphertext: reads fetch ciphertext at payload offset and decrypt into caller qiov; writes copy caller data to the bounce buffer, encrypt, and write ciphertext. Request alignment is set to the crypto sector size, length subtracts payload offset, and truncate adds payload offset with overflow checks.

The LUKS-specific sections implement probing, measuring required/fully allocated size, image-specific info reporting, keyslot amend options, permission tightening during key updates, and child permission compatibility behavior. The registered format driver is `luks`, with create, create-opts, truncate, measure, get-info, amend, reopen, read/write, and strong runtime option support.
