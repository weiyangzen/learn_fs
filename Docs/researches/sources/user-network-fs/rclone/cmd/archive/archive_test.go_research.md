# sources/user-network-fs/rclone/cmd/archive/archive_test.go

Purpose: end-to-end tests for archive create/list/extract flows over local, remote, and memory backends. It validates destination checking, archive creation in many formats, listing archive entries, purging source, extracting back, and comparing restored listings.

Important helpers: `TestCheckValidDestination`, `testArchiveRemote`, `testArchive`, `TestIntegration`, and `TestMemory`. State is created through `fstest.NewRun`, local/remote files, generated archives, and purge operations. Dependencies include `mholt/archives`, local/memory backends, operations, and archive subpackages. Risks covered include format support, directory entries, file sizes, subdirectory extraction, and source/destination direction. Gaps include dry-run, metadata preservation, filters, stdout archive output, and error paths. Test signal is strong for supported formats and standard file restore semantics.
