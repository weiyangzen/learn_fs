# sources/sync-backup/borg/src/borg/helpers/parseformat.py

## Purpose
Large helper module for parsing CLI values and repository locations, formatting archive/item/diff output, JSON serialization, placeholder replacement, text validation, path safety actions, and display utilities.

## Important APIs, Types, And Functions
Primitive helpers include `octal_int`, `bin_to_hex`, `hex_to_bin`, `safe_decode`, `safe_encode`, `remove_surrogates`, `binary_to_json`, `text_to_json`, `join_cmd`, `eval_escapes`, `decode_dict`, and `interval`. CLI parsers include `CompressionSpec`, `ChunkerParams`, `FilesCacheMode`, `PathSpec`, `FilesystemPathSpec`, `SortBySpec`, size parsers/formatters, relative time and text validators, tag/archive/comment validators, `Highlander`, and `MakePathSafeAction`. Formatting types include `DatetimeWrapper`, `PlaceholderReplacer`, `Location`, `BaseFormatter`, `ArchiveFormatter`, `ItemFormatter`, `DiffFormatter`, `BorgJsonEncoder`, and JSON/dump helpers.

## Control Flow
Validators convert strings to typed values or raise `ArgumentTypeError`/`ArgumentError`. `CompressionSpec` parses nested compression forms and lazily builds compressor objects. `ChunkerParams` accepts fixed, fail, default, buzhash64, and legacy buzhash forms with bounds checks. `Location` replaces placeholders, then parses legacy ssh/rest/file forms, borgstore-handled schemes, or local paths; canonical paths redact credentials for external schemes. Formatters precompute requested keys from format strings and lazily load archive metadata or file content hashes only when requested.

## State And Persistence
`replace_placeholders` is a module-level `PlaceholderReplacer` with mutable overrides. YAML representers and jsonargparse type registrations are global side effects at import. Formatter instances cache archive objects, requested keys, and condition hashes. JSON helpers do not persist directly but serialize repository/cache/archive state for command output.

## Dependencies And Integration Points
Tightly integrated with constants, argument parsing, msgpack timestamps, time helpers, filesystem path safety, platform display width, archive/repository/cache classes, borgstore URL handoff, manifest sorting keys, compression registry, and command output modes.

## Risks And Edge Cases
This module is security-sensitive around path sanitization, URL credential redaction, JSON-safe surrogate handling, and shell command display. `Location` treats several schemes as pass-through, so canonicalization differs by proto. Formatter hash keys can trigger expensive archive reads. Text validators must reject surrogate escapes for user-visible metadata. Placeholder replacement can inject current time/user/uuid and must validate unknown placeholders.

## Test Signals
Existing parseformat tests should cover compression grammar, chunker bounds, file-size parsing/formatting, location variants and credential redaction, placeholder validation, validators, JSON encoding of bytes/surrogates/timestamps, formatter key help and lazy calls, hash/fingerprint calculations, display-width truncation, and action classes.
