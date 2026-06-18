## sources/security-integrity/encfs/src/constants.rs

Purpose: Shared constants for EncFS configuration defaults and buffer sizing.

Important APIs and values: `DEFAULT_SALT_SIZE` 20 bytes, `DEFAULT_KDF_ITERATIONS` 100000, Argon2 defaults `DEFAULT_ARGON2_MEMORY_COST` 64 MiB, `DEFAULT_ARGON2_TIME_COST` 3, `DEFAULT_ARGON2_PARALLELISM` 4, `DEFAULT_CONFIG_VERSION` 20260101, `DEFAULT_BLOCK_SIZE` 4096, `FILE_BUFFER_SIZE` 128 KiB, `V5_MIN_SUBVERSION` 20040813, and `XML_BASE64_LINE_LEN` 76.

Control flow: none; constants are consumed by config creation/validation, file operations, and legacy compatibility logic. State and persistence: values shape newly generated config files and runtime buffers, so changes are persistent for new volumes. Dependencies are none. Integration is visible in `EncfsConfig::standard_v7`, `test_default`, V5 version checks, and file IO paths. Risks: changing defaults affects compatibility, security cost, and performance; Argon2 defaults in particular alter unlock latency and memory pressure.
