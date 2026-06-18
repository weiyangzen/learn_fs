# sources/sync-backup/git-crypt/key.hpp

Purpose: declares git-crypt key file structures, constants, exceptions, and key-name validation.

Important APIs/types/functions: constants `HMAC_KEY_LEN`, `AES_KEY_LEN`, and `KEY_NAME_MAX_LEN`; `struct Key_file` with nested `Entry`, exception tags `Malformed` and `Incompatible`, versioned entry map accessors, load/store/generate helpers, key name getters/setters, and `validate_key_name`.

Control flow: no direct implementation flow; the declarations encode the modern key file model of one optional key name and one or more versioned AES/HMAC entries.

State/persistence behavior: `Entry` contains raw AES and HMAC key arrays. `Key_file` owns a version-sorted map and optional key name. Serialized files are binary and versioned.

Dependencies/integration: included by crypto for key-length constants and by command code for key management. `Key_file::Entry` is the bridge between stored key material and encryption commands.

Risks/test signals: public constants are file-format/security contract. Tests should detect accidental changes to key lengths, format version behavior, and named-key validation rules.
