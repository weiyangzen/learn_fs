# sources/storage-engines/tikv/components/sst_importer/src/import_file.rs

Purpose: manages on-disk SST upload files, file naming, validation, deletion, ingestion preparation, checksum verification, and listing.

Important APIs and types: `ImportPath` holds `save`, `temp`, and `clone` paths. `ImportFile` writes an uploaded SST to temp while tracking CRC32 and renames it to save on finish. `ImportDir<E>` owns root, `.temp`, and `.clone` directories and provides path, create, delete, exist, validate, API-version check, ingest, checksum, and list operations. `sst_meta_to_path`, `sst_meta_to_path_v1`, and `parse_meta_from_path` encode/decode SST filenames. `API_VERSION_2` is the current filename version.

Control flow: `ImportDir::new` clears and recreates temp/clone dirs. `ImportFile::create` uses `DataKeyManager` encrypted writer when present or `create_new` file open otherwise. `append` writes bytes and updates CRC. `finish` validates CRC, syncs file, rejects existing save path, links encryption metadata if needed, renames temp to save, and leaves directory sync to `ImportPath::save` for callers using that path helper. `Drop` cleans unfinished temp files and encryption metadata. `join_for_read` prefers v2 filenames if they exist and falls back to v1 for old TiKV files. `ingest` checks API compatibility, prepares hard-linked/copied clone files, groups paths by CF, and calls `ingest_external_file_cf` with `force_allow_write`.

State and persistence behavior: creates/removes directories and files under importer root, syncs file contents, renames temp to durable save path, creates clone files for ingestion, removes encryption metadata on cleanup, and reads SST metadata/checksums. API compatibility may scan SST key ranges against TiDB range complements.

Dependencies and integration points: used by `SstImporter` and writers. Depends on engine `SstReader`/ingestion traits, file system helpers, encryption `DataKeyManager`, `keys`, `api_version`, import protobuf metadata, UUID, CRC32, and importer metrics.

Risks: file lifecycle must be crash-safe; temp/clone dirs are wiped at `ImportDir::new`. `finish` does not sync the directory after rename, while `ImportPath::save` does. `check_api_version` unwraps its result inside `ingest`, and incompatible version panics rather than returning an error. Filename parsing supports legacy formats with missing CF/API version, so callers must handle partially populated metadata. `Drop` cleanup can race with external use if ownership semantics are misused.

Test signals: tests cover v2 path encoding/decoding, legacy path parsing, v2/v1 read fallback, and feature-gated SST path handling with and without encryption key manager.
