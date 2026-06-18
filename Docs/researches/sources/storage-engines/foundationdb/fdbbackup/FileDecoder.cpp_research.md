# sources/storage-engines/foundationdb/fdbbackup/FileDecoder.cpp

## Purpose
Implements `fdbdecode`, a tool for listing and decoding FoundationDB backup log/range files with filters for file name, key prefix, and version range.

## Important APIs, Types, and Functions
`DecodeParams` holds CLI/config state and filtering helpers. `parsePrefixesLine()` and `parsePrefixFile()` parse hex prefix filters. `DecodeProgress` loads one mutation log file and reconstructs complete `VersionedMutations` from chunks. `DecodeRangeProgress` decodes range files. `process_file()`, `process_range_file()`, `getRangeFiles()`, and `decode_logs()` handle selection and output.

## Control Flow
`main()` parses options, validates version filters, configures tracing/TLS/blob credentials/knobs, initializes Flow, and runs `decode_logs()`. The orchestrator opens the container, lists files, filters logs/ranges, optionally lists only, then sequentially decodes selected log files and range files, printing matching mutations or key-values.

## State and Persistence Behavior
State is mostly in memory: decoded blocks, mutation chunks by version, filters, and selected file lists. `--save` writes downloaded files locally with container-derived paths. Trace logs are produced when logging is enabled. The source database is not modified.

## Dependencies and Integration Points
Depends on backup containers, filesystem snapshot metadata, backup TLS/blob credentials, optional encryption key file, Flow runtime, trace logging, mutation/range decode helpers, client knobs, `Decode.cpp`, and `FileConverter.h` options. Built as `fdbdecode`; `EXCLUDE_MAIN_FUNCTION` provides a small test main.

## Risks
Reads whole files into memory. Range decoding casts to `BackupContainerFileSystem*` without a visible null check. `--save` can overwrite local paths matching container names. Prefix parsing inherits `decode_hex_string` risks. Filtering bugs can hide relevant mutations/ranges.

## Test Signals
Current `FileDecoderTests` checks version-filter validity. Broader tests should cover CLI parsing, prefix filters, log/range fixtures, list-only mode, save behavior, encryption/TLS/blob setup, corrupt files, and filesystem vs non-filesystem containers.
