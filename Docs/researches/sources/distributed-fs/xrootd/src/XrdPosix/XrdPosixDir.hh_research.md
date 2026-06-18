## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixDir.hh

Purpose: declares `XrdPosixDir`, the remote directory object stored in the XrdPosix descriptor table.

Important APIs/types: derives from `XrdPosixObject`; contains `XrdPosixAdmin DAdmin`, `XrdCl::DirectoryList *myDirVec`, `dirent64 *myDirEnt`, optional `struct stat *myBuf`, counters, and error state. Provides `dirNo(DIR*)`, `getEntries`, `getOffset`, `setOffset`, `nextEntry`, `Open`, `StatRet`, `rewind`, `Status`, `Unread`, and `Who(XrdPosixDir**)`.

Control flow: descriptor table lookup uses `Who()` to downcast. `DIR*` values are synthesized from the object FD, and `dirNo()` reverses that encoding.

State and persistence: all state is in-memory per open directory. Destructor deletes the directory list and frees the synthetic dirent buffer.

Dependencies/integration: includes `XrdPosixAdmin.hh` and `XrdPosixObject.hh`. It is used by `XrdPosixXrootd` directory wrappers and `XrdPosix.cc` dispatchers.

Risks: synthetic `DIR*` representation depends on callers never passing it to native libc. `setOffset()` does not validate bounds. `maxDlen=256` can truncate longer protocol names.

Test signals: descriptor-table `Who()` behavior; close cleanup; seek/tell offsets beyond list size; concurrent directory access locking via base object.
