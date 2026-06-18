# sources/sync-backup/borg/docs/usage/general/resources.rst.inc

Purpose: explains CPU, memory, disk, temporary-file, and network resource use for Borg operations.

Important APIs and control flow: splits client/server resource responsibilities. Create is CPU-heavy for chunking, hashing, compression, and encryption; extract/check read/decrypt/decompress; caches and repository indexes scale with chunk/file counts; remote use adds SSH transport CPU and network traffic.

State and persistence: local cache files store chunks and files indexes plus per-archive indexes; temporary directories can hold large FUSE/cache or remote data; repository indexes live server-side.

Dependencies and integration points: files cache, chunks index, repository index, compression levels, chunker parameters, FUSE mount cache, SSH transport, TMPDIR/TEMP/TMP, and server environment setup.

Risks: large repositories can exhaust RAM, cache disk, or remote `/tmp`; high compression can waste CPU/RAM; single-threaded Borg operations do not exceed one core except transport helpers.

Test signals: performance tests for cache/index scaling, remote TMPDIR behavior, compression memory profiles, and network throughput under client/server mode.
