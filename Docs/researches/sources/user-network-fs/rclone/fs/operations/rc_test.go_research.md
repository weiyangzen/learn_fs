# Research: sources/user-network-fs/rclone/fs/operations/rc_test.go

## sources/user-network-fs/rclone/fs/operations/rc_test.go

Purpose: endpoint-level tests for `fs/operations/rc.go`. `rcNewRun` constrains tests to local remotes, creates a fixture, finds the registered call, and seeds the fs cache. Tests cover about/cleanup, copy/move file, copyurl, delete/deletefile, list/stat, tier operations, mkdir/rmdir/rmdirs/purge, size, publiclink, fsinfo, multipart uploadfile, backend command, disk usage, check, hashsum, single-file hashsum, and hashsumfile.

Control flow sets up local/remote files, invokes `call.Fn(context.Background(), rc.Params{...})`, then asserts returned params and final listings. State and persistence are fixture filesystem writes, cache entries, HTTP test servers, multipart request bodies, and generated remote objects. Dependencies include `fstest`, `cache`, `hash`, `diskusage`, `rest.MultipartUpload`, and `httptest`. Integration points verify rc parameter names and output shapes expected by API clients. Risks signaled include unsupported backend features, non-local remote skips, map/slice type shapes after `rc.Reshape`, check report ordering requiring sorting, and hash support variations. Test signal is strong for externally visible rc behavior.
