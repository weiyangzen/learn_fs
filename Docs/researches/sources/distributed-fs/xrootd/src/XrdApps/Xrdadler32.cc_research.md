# sources/distributed-fs/xrootd/src/XrdApps/Xrdadler32.cc

Purpose: implements `xrdadler32`, computing or retrieving Adler-32 checksums for stdin, local files, virtual-mapped paths, and `root://` URLs.

Important APIs/types/functions: `fSetXattrAdler32` writes checksum metadata using XRootD checksum xattrs and removes old native attrs; `fGetXattrAdler32` has native and XRootD xattr variants; `getchksum` asks a remote server for `xroot.cksum`; `main` selects local versus remote path behavior and computes with zlib `adler32`.

Control flow: `main` handles `-h`, converts arguments through `XrdPosixXrootPath` when possible, uses local open/stat/read for non-root paths or stdin, consults cached xattrs before reading local files, stores new xattrs after computing, and for remote files first tries server checksum metadata. If absent, it opens through `XrdPosixXrootd` and reads until file size is covered.

State and persistence: can persist local checksum metadata in XRootD checksum xattr format and removes the older `user.checksum.adler32` attr after migration. Remote state is read-only.

Dependencies and integration points: depends on zlib, XrdPosix path/IO wrappers, XrdCks checksum xattr types, and platform xattr APIs.

Risks: fixed path/checksum buffers use `strcpy`; long URLs or paths can overflow. Native xattr reader assumes `attr_val[8]` exists even if fewer than 9 bytes are returned. Remote fallback has a comment for an XrdClEC regression and bounds read length against stat size. `getchksum` returns `char`, which is too narrow for checksum length/error semantics.

Test signals: stdin checksum, local cache hit/miss/stale mtime, xattr migration, root URL server-checksum success/failure, virtual mount translation, remote read fallback, and permission/access errors.
