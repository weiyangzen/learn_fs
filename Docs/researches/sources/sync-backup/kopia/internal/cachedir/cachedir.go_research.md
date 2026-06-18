# sources/sync-backup/kopia/internal/cachedir/cachedir.go

Purpose: writes the `CACHEDIR.TAG` marker that tells backup/indexing tools that a directory contains disposable cache data.

Important APIs/types/functions: `CacheDirMarkerFile`, `CacheDirMarkerHeader`, `WriteCacheMarker`, and private `cacheDirMarkerContents`.

Control flow: `WriteCacheMarker` no-ops for an empty directory string, stats the target marker, accepts any existing file at least as large as the Kopia marker contents, otherwise creates/truncates the marker file, writes the fixed tag text, and closes it.

State and persistence behavior: persistent state is a file named `CACHEDIR.TAG` under the cache directory. The function does not create the parent directory and treats non-`IsNotExist` stat errors as unexpected.

Dependencies/integration: uses `os`, `filepath`, and `pkg/errors`. Cache directory setup code can call this after ensuring the directory exists.

Risks/test signals: a too-large but wrong marker file is accepted without validating the header. Error paths include stat, create, write, and close failures. No tests are listed for this file in the work item.
