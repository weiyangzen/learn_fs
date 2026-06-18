# sources/storage-engines/rocksdb/build_tools/getdeps_fallback_mirror.py research

Purpose: `getdeps_fallback_mirror.py` pre-downloads selected getdeps packages from fallback mirrors when canonical GNU mirrors are unreliable. It reads package manifests from Folly/getdeps metadata and prepares validated downloads for a single build.

Important APIs: constants define timeouts, chunk size, maximum download size, known mirror patterns, and packages to check. Functions include `sha256_file()`, `parse_manifest()`, `file_size()`, `get_fallback_mirrors()`, `download_url()`, `prepare_download()`, and `main()`.

Control flow: `main()` expects `download_dir`, `cache_dir`, and `manifests_dir`, creates the first two, loops over `PACKAGES_TO_CHECK`, parses each manifest's `[download]` URL and sha256, verifies a known fallback mirror exists, and calls `prepare_download()`. `prepare_download()` validates any existing download, repairs from cache when possible, tries mirror URLs in order, verifies SHA256 after each download, copies successful downloads into cache, and reports ready/checked counts.

State and persistence: it writes package files into `download_dir`, opportunistically writes/copies cache files in `cache_dir`, and uses temporary `.tmp` files that are removed on success or failure. Invalid existing files are deleted.

Dependencies and integration: it uses Python stdlib only: `configparser`, `hashlib`, `os`, `shutil`, `sys`, and `urllib.request`. It integrates with RocksDB/Folly getdeps workflows that expect downloaded files named `{package}-{basename(url)}`.

Risks and test signals: cache use is explicitly not concurrency-safe without external locking. Only known GNU mirror URL patterns and selected packages are handled. The 50 MiB cap can reject legitimate future package sizes. Tests should mock manifests, mirrors, checksum mismatch, partial download cleanup, existing valid downloads, cache repair, and network failures.
