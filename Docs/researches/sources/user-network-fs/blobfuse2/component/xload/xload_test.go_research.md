## sources/user-network-fs/blobfuse2/component/xload/xload_test.go

Purpose: Main test suite for xload configuration, downloader construction, lifecycle, and cached open behavior.

Important APIs and flow: Setup creates random local cache and fake storage directories, reads a minimal read-only xload+loopback config, and constructs xload over loopback. Tests cover defaults, read-only enforcement, block size from component and CLI stream config, path fallback from file cache, missing/same-as-mount/nonempty path errors, mode parsing, allow-other permissions, unsupported modes, priority, block pool start failure, default `XBase`, downloader/chain creation, download error paths, start/stop preloading, opening already downloaded files, and on-demand downloads after remote data appears.

State and dependencies: Uses loopback as fake storage, real temp directories, config global state, small block sizes to force chunking, wall-clock sleeps, and recursive MD5 validation.

Risks and test signals: Tests reset global config frequently and rely on sleeps for async preloading. They cover many user-facing config failures and integration behavior but do not stress concurrent opens, stop races, or file handle closure semantics.
