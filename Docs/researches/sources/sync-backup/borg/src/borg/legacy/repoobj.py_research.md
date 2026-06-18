# sources/sync-backup/borg/src/borg/legacy/repoobj.py

Purpose: defines `RepoObj1`, the Borg 1.x object codec used for legacy reads and transfers. It stores encrypted compressed payload directly, without the Borg 2 object header or separate encrypted metadata envelope.

Important APIs/types: `extract_crypted_data` returns raw data for crypto detection. `format` compresses with legacy lz4 unless precompressed data is supplied, encrypts with `key.encrypt`, and returns encrypted bytes. `parse` decrypts, detects compression from the compressed prefix, optionally decompresses and verifies `key.assert_id`, and can return compressed data through `want_compressed`. `parse_meta` is intentionally unavailable.

Control flow/state: instances keep only `key` and a legacy-mode compressor. Format asserts empty metadata and valid parameters; parse rejects invalid decompress/want-compressed combinations and builds synthetic compression metadata (`ctype`, `clevel`, `csize`) from the payload.

Dependencies/integration: used by upgrade/transfer code and re-exported from modern `borg.repoobj`. Relies on `Compressor.detect`, `get_compressor`, constants, and the `authenticated_no_key` workaround.

Risks: metadata-only parsing is impossible. Important validation is partly assertion-based. `AUTHENTICATED_NO_KEY` disables ID verification. Object type is not persisted by this legacy format.

Test signals: legacy lz4/zlib round trips, compressed reuse paths, ID mismatch failures, workaround behavior, and `parse_meta` raising `NotImplementedError`.
