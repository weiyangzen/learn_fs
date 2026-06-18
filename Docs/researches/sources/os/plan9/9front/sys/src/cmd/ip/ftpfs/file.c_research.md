# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ftpfs/file.c

Temporary file/cache layer for `ftpfs`. Each remote file can have a `File` cache with the first 1024 bytes in memory and larger content in a temporary `/tmp/ftpXXXXXXXXXXX` file.

Provides cached read/write, dirty/clean flags, LRU-style reuse of clean cache slots, and cleanup of temp files. `uncachedir` evicts clean cached files in sibling directories when the temporary-file count grows.

This layer is used by the 9P front end to buffer reads from FTP and stage writes before uploading on clunk.
