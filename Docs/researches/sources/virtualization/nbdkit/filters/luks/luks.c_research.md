# File Research: sources/virtualization/nbdkit/filters/luks/luks.c

Implements the nbdkit-facing LUKS filter. Configuration requires `passphrase=`, read through `nbdkit_read_password()`. Unload scrubs and frees the passphrase, with a note that locked memory would be preferable.

Each connection allocates a handle and calls `load_header()` in prepare. Export size is upstream size minus the LUKS payload offset. The filter disables extents, trim, fast zero, and native zero, and asks nbdkit to emulate cache through decrypted reads.

`luks_pread()` maps logical offsets into encrypted payload sectors, handling unaligned head/tail reads by reading a full sector, decrypting it, and copying the requested slice. Aligned body reads decrypt one sector at a time.

`luks_pwrite()` encrypts writes. Unaligned head/tail writes perform read-modify-write of full sectors under a global mutex; aligned body writes encrypt sector buffers directly. All encryption/decryption uses cipher handles from `luks-encryption.c`.
