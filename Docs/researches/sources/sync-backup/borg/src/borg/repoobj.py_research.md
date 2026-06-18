# sources/sync-backup/borg/src/borg/repoobj.py

Purpose: defines the Borg 2 repository object envelope with a fixed header, separately encrypted metadata and data, compression metadata, type validation, and metadata-only parsing.

Important APIs/types: `RepoObj`, `OBJ_MAGIC`, `OBJ_VERSION`, `REPOOBJ_HEADER_SIZE`, `obj_header`, and `ObjHeader`. Methods are `extract_crypted_data`, `id_hash`, `format`, `parse_meta`, and `parse`. `RepoObj1` is re-exported for compatibility.

Control flow/state: `format` mutates metadata with object `type` and compression fields, compresses or accepts precompressed data, encrypts metadata and data separately, and prefixes header. `parse_meta` validates header and decrypts only metadata. `parse` validates full size, decrypts, optionally decompresses, handles `psize`, and verifies chunk ID unless the workaround is active.

Dependencies/integration: used by repositories, manifest/archive serialization, cache and transfer code. `Repository.get(read_data=False)` returns enough bytes for `parse_meta`.

Risks: supplied metadata dict is mutated. Assertions encode important preconditions. Metadata-only reads depend on exact header/size behavior. Non-decompress compressed reuse paths skip ID verification.

Test signals: invalid header errors, type mismatch, metadata-only parsing, compressed/precompressed round trips, obfuscation payload size, ID verification, and legacy import compatibility.
