# sources/sync-backup/borg/src/borg/testsuite/archiver/debug_cmds_test.py

Purpose: integration tests for Borg's `debug` subcommands: profiling conversion, dumping archive/repository objects, raw object put/get/delete, object format/parse, manifest/archive JSON dumps, and debug environment info.

Important APIs/types/functions: tests use `pstats.Stats`, JSON, shared command/file helpers, `Compressor`, and constants such as `ROBJ_ARCHIVE_STREAM` and `ITEM_KEYS`. Commands covered include `debug convert-profile`, `dump-archive-items`, `dump-repo-objs`, `id-hash`, `put-obj`, `get-obj`, `delete-obj`, `format-obj`, `parse-obj`, `dump-manifest`, `dump-archive`, and `debug info`.

Control flow: profile tests create archives with `--debug-profile`, convert formats, and load resulting pstats. Dump tests create archives and assert output directories contain generated object/item files. Raw object tests compute an ID hash, put a file as an object, retrieve it, compare bytes, delete it, and handle repeated/invalid deletes. Format/parse tests build data and metadata JSON, format a repo object with compression, put/get/parse it, and validate plain data plus metadata including compressed size/type/level. Type-respecting tests ensure metadata `type` survives formatting. Manifest/archive dump tests write JSON files and verify expected keys. `debug info` checks for Python information.

State and persistence behavior: writes profile files, dump directories, repo object files, data/meta JSON files, and output objects in fixture directories. Mutates repository object storage via debug commands.

Dependencies and integration points: covers debug command plumbing, repository object serialization, compression metadata, manifest/archive JSON dumping, profiling hooks, and constants defining object/item schemas.

Risks: debug commands expose low-level internals, so tests are tightly coupled to object metadata names and repository object formatting. Loading pstats is only safe because test-created files are trusted.

Test signals: validates debug tooling remains operational for diagnostics and low-level object inspection/manipulation.
