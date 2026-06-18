# sources/sync-backup/borg/src/borg/crypto/file_integrity.py

Purpose: provides wrappers that hash file contents and contextual part names while reading/writing, enabling integrity checks for local cache/index-like files and detached `.integrity` sidecars.

Important APIs: `FileLikeWrapper` delegates file operations. `FileHashingWrapper` updates a hash during `read`/`write`, hashes file length on clean exit unless `pure_hash`, and exposes `hexdigest`, `update`, and `hash_length`. `SHA256FileHashingWrapper` selects SHA-256. `IntegrityCheckedFile` wraps a path or override fd, loads optional integrity JSON, hashes the basename as context, verifies or stores digests for named parts, and exposes `integrity_data` after writes. `DetachedIntegrityCheckedFile` reads/writes `<path>.integrity` files.

Control flow and state: reads parse integrity data when supplied, then each `hash_part(partname, is_final)` includes part name and current length in the digest. On clean context exit, the `"final"` part is checked/stored. Write mode records digests in memory and serializes JSON; read mode raises `FileIntegrityError` on parse or digest mismatch.

Dependencies and integration: used by cache code for files-cache integrity. Depends on `hashlib`, JSON, `hmac.compare_digest`, `Path`, Borg `IntegrityError`, and logging.

Risks: seeking/skipping data is explicitly unsafe because skipped bytes are not hashed. Integrity context includes basename but not directory, allowing supported moves while detecting filename-context changes. Unknown algorithms warn and skip verification rather than failing; malformed integrity data raises.

Test signals: cover read/write round trips, basename hashing, final digest mismatch, part digest mismatch, malformed JSON, unknown algorithm handling, detached sidecar behavior, override fd handling, and seek-to-end length hashing.
