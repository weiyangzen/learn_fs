## sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/CMakeLists.txt

Purpose: builds the core NFS protocol object libraries.

APIs and flow: `nfsproto_STAT_SRCS` always includes NFSv4 compound/op handlers and common protocol helpers. When `USE_NFS3` is enabled it appends MOUNT procedures and NFSv3 handlers such as access, commit, create, fsinfo, read/write, readdir, link, rename, and setattr. It creates `nfsproto` and `nfs4callbacks` object libraries with sanitizer and `-fPIC` settings, plus optional LTTng generated-header dependency.

State/dependencies: build-time source manifest backing descriptor tables in `nfs_worker_thread.c`. No runtime persistence.

Risks/tests: missing handlers under `USE_NFS3` break descriptor references. Test builds with and without NFSv3, NFSv4 callbacks, sanitizer settings, and LTTng enabled.
