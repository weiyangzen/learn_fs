# sources/object-store/rustfs/crates/filemeta/examples/dump_versions.rs

Purpose: small debug CLI for listing all versions in an `xl.meta` file.

Important APIs and flow: `main` reads the file path argument, loads bytes, parses with `FileMeta::load`, converts with `into_file_info_versions("debug-bucket", "debug-object", true)`, and prints path, version count, and per-version ID/delete/latest/size/mod-time fields.

State and persistence: read-only over an existing xl.meta file. It uses placeholder volume/object labels for display and conversion context.

Dependencies and integration: depends on public `rustfs_filemeta::FileMeta`. It exercises the same version conversion path object-store listing/debugging uses.

Risks: it does not expose all metadata, erasure, tiering, or replication fields; pair with `dump_fileinfo` for deeper object inspection. Placeholder names may hide path-sensitive issues.

Test signals: no direct tests; success depends on `FileMeta::load` and `into_file_info_versions` compatibility tests in the library.
