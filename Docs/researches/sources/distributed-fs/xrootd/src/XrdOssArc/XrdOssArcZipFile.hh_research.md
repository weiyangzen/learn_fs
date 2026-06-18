# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcZipFile.hh

Purpose: declares a small libzip-backed file facade for archive members. It is not an OSS subclass; it is an internal helper used by `XrdOssArcFile` when the logical open targets a member inside an archive.

Important APIs/types: public methods are `Open(member)`, `Read(buff, offset, blen)`, `Stat(struct stat&)`, `Stat(member, struct stat&)`, and `Close()`. The constructor reports initialization through an `int& rc`, and the destructor closes all libzip resources. Private helpers `zipEmsg()` and overloaded `zip2syserr()` convert/log libzip errors.

State/control behavior: the class stores archive-level stat in `zFStat`, path/member strings, `zip_t*`, `zip_file_t*`, `zOffset`, `zSeek`, and `zEOF`. `zSeek` controls random-read behavior and `zEOF` suppresses repeat reads after EOF. There is no locking; instances are per-open and expected to be single-client.

Dependencies/integration: forward declares libzip structs and `stat`, keeping libzip details out of callers. Risks include constructor error reporting rather than throwing, raw pointer ownership, and no copy prevention despite owning C handles. Test signals: lifecycle under failed constructor/open, member switching, stat with and without active subfile, and correct negative errno mapping.
