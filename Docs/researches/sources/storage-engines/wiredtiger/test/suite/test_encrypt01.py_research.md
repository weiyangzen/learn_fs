# sources/storage-engines/wiredtiger/test/suite/test_encrypt01.py

Purpose: broad encryption/compression matrix test for system-level and per-file encryption.

Important APIs and control flow: scenarios combine file/table URI, encryptors (`none`, `nop`, `rotn`, `rotn-none`, `sodium`), compressors, and early extension loading. `conn_extensions` loads encryptor and compressor extensions with skip-if-missing. `conn_config` sets system encryption and optional log compressor. The test creates the object with file encryption and block compressor, writes 4999 deterministic random keys/values, reopens, and verifies every value.

State and persistence: reopen forces encrypted and compressed pages to disk and back. Random seed 0 makes verification deterministic.

Dependencies and integration: uses extension loading, sodium test key, rotn key IDs, log compression, block compression, and cursor search.

Risks and test signals: high scenario count catches extension-load ordering, encryption inheritance, compression/encryption stacking, and readback corruption.
