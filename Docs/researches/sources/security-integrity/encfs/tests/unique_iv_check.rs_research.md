# sources/security-integrity/encfs/tests/unique_iv_check.rs

Purpose: ensures V6 XML configs with `<uniqueIV>0</uniqueIV>` are accepted by `EncfsConfig::load`.

Important APIs/types/functions: writes an inline XML config to a temp file and calls `EncfsConfig::load`, then checks `config.unique_iv == false`.

Control flow: the test builds an XML string with AES-192, block name encoding, `uniqueIV` 0, chained name IV 1, external IV chaining 0, no MAC bytes, PBKDF2 fields, and encoded key/salt data. It writes the file, loads it, removes it, and asserts successful parse with false unique IV.

State and persistence: temporary XML file only.

Dependencies and integration points: validates config parser and validation rules used by reverse mode, because `encfsr` requires `unique_iv=false`.

Risks: only parsing is tested; it does not derive the cipher or mount/read with this inline config. XML fixture key material is copied from a test source.

Test signals: guards against overly strict validation rejecting reverse-compatible configs.
