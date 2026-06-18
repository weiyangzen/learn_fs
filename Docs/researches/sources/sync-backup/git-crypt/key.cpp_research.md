# sources/sync-backup/git-crypt/key.cpp

Purpose: serialization, parsing, generation, storage, and validation for git-crypt symmetric key files.

Important APIs/types/functions: `Key_file::Entry` constructor, `load`, `load_legacy`, `store`, `generate`; `Key_file` methods `get_latest`, `get`, `add`, `load_legacy`, `load`, `load_header`, `store`, `load_from_file`, `store_to_file`, `store_to_string`, `generate`, `latest`; and `validate_key_name`.

Control flow: modern key files start with `\0GITCRYPTKEY` plus format version 2, then optional header fields such as key name, an end marker, and one or more entry records. Entry records are field/value encoded with critical odd field IDs causing `Incompatible` and safe even unknown fields skipped within a maximum length. Legacy loading reads one AES key and one HMAC key as version 0 and rejects trailing data. Generation selects version 0 for empty files or latest+1 and fills AES/HMAC keys with random bytes.

State/persistence behavior: `Key_file` stores entries in a descending `std::map` keyed by version and optional key name. `store_to_file` calls `create_protected_file`, writes binary key data, and checks close status. Key bytes are held in memory; constructors zero initialize, but entries are not explicitly wiped on destruction.

Dependencies/integration: uses big-endian helpers, random bytes, explicit memset, protected file creation, and key-name validation. Command handlers load/store internal keys, exported symmetric keys, migrated legacy keys, and GPG-wrapped per-version key files.

Risks/test signals: malformed/incompatible parsing is security-critical. Key-name validation currently dereferences `key_name`, so callers must not pass null except where logic bypasses validation for default keys. Tests should cover modern and legacy round trips, unknown critical/noncritical fields, maximum field lengths, invalid key names, multiple versions ordering, protected file permissions, and malformed/truncated inputs.
