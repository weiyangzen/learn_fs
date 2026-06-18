# sources/distributed-fs/xrootd/src/XrdOss/XrdOssMioFile.hh

## Purpose
Defines the object representing one mapped file in the OSS mmap manager.

## Important APIs, types, and functions
`XrdOssMioFile` is a friend of `XrdOssMio`. The public `Export(void **Addr)` returns the mapping base address via `Addr` and the mapped size as `off_t`. The constructor copies a hash name and initializes use count, list pointer, and size. The destructor is implemented in `XrdOssMio.cc` and unmaps the file when POSIX mapped files are available.

## Control flow
Objects are created by `XrdOssMio::Map()`, stored in `MM_Hash`, linked into permanent or idle lists, exported to file readers, recycled through `XrdOssMio::Recycle()`, and destroyed when reclaimed from the hash.

## State and persistence
Each object stores `Next`, device, inode, status flags, use count, mapped base, size, and a fixed-size hash name. State is in memory only.

## Dependencies and integration points
Requires system `dev_t`, `ino_t`, and `off_t`. It intentionally exposes little beyond `Export()`; lifecycle management stays in `XrdOssMio`.

## Risks and test signals
The constructor uses `strcpy()` into `HashName[64]`; safety depends on `XrdOssMio::Map()` generating bounded keys. Tests should check export size/address, destructor unmapping through reclaim, and that hash names generated from large platform `dev_t/ino_t` values fit.
