# File Research: sources/virtualization/nbdkit/filters/luks/luks-encryption.h

Public internal interface for the LUKS filter’s crypto layer. Defines `LUKS_SECTOR_SIZE` as 512 and forward-declares `struct luks_data`.

Declares `load_header()`, `free_luks_data()`, `get_payload_offset()`, `create_cipher()`, `do_decrypt()`, and `do_encrypt()`.

The comments document that `load_header()` may perform many upstream reads and that sector numbers are used for IV generation.
