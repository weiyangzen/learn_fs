# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcZipFile.cc

Purpose: implements read-only access to a member inside a zip archive while presenting stat/read behavior needed by `XrdOssArcFile`. It converts libzip errors into negative errno values and logs archive/member-specific diagnostics.

Important APIs/functions: the constructor opens the archive path read-only, snapshots `stat`, stores the path, and converts the fd to `zip_t` with `zip_fdopen(ZIP_CHECKCONS)`. `Open(member)` closes any previous member, stores the member name, opens it with `zip_fopen`, and currently assumes seekability. `Read()` seeks if needed, reads with `zip_fread`, tracks `zOffset`, and returns EOF after short reads. `Stat()` variants copy archive `stat` then replace inode/size when libzip supplies them. `Close()` closes member state; destructor closes member/archive and frees strings. `zip2syserr()` maps libzip error codes.

State/control: mutable state includes archive pointer, subfile pointer, member name, offset, seekability, and EOF. Persistence is entirely the zip archive on disk.

Dependencies/integration: depends on libzip, `XrdSysFD_Open`, `XrdSysError`, and `XrdOucString`. Risks include assuming compressed members are seekable because older libzip lacks `zip_file_is_seekable`, EOF state reset only on seek/open, mixed sign convention in constructor `rc = -errno`, and `zip_error_fini()` ownership expectations. Tests should cover missing archive/member, stat propagation, random reads, sequential reads, compressed member behavior, and destructor cleanup after failed opens.
