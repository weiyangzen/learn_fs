# File Research: sources/windows/dokany/dokan_fuse/src/dokanfuse.cpp

Implements the high-level Dokan FUSE runtime wrapper and Dokan callback table.

Key areas:
- DLL initialization stores module instance and disables per-thread attach notifications.
- Defines `the_impl` to recover `impl_fuse_context` from `DokanOptions->GlobalContext`.
- Static Dokan callbacks wrap operations with `impl_chain_guard`, debug logging, and errno-to-NTSTATUS conversion:
  - create/open, cleanup, close;
  - read/write/flush;
  - get file info, find files;
  - delete file/directory;
  - move, lock/unlock;
  - set EOF/allocation/attributes/times;
  - disk free space, volume info;
  - mounted/unmounted.
- `dokanOperations` table wires those callbacks into Dokan.
- `do_fuse_loop`:
  - computes file/dir masks;
  - creates `impl_fuse_context`;
  - fills `DOKAN_OPTIONS`;
  - maps FUSE options to Dokan options such as mount manager, removable, network, write protect, debug, stderr, IPC batching;
  - converts mountpoint to wide string;
  - dynamically loads Dokan through `fuse_chan::init`;
  - calls `DokanMain`.
- `fuse_chan::init`:
  - loads `dokan<major>.dll`;
  - checks `DokanVersion`;
  - resolves `DokanInit`, `DokanShutdown`, `DokanMain`, `DokanUnmount`, and `DokanRemoveMountPoint`;
  - calls `DokanInit`.
- FUSE API emulation:
  - parses library options through `fuse_opt_parse`;
  - implements `fuse_mount`, `fuse_unmount`, `fuse_new`, `fuse_exit`, `fuse_destroy`, `fuse_setup`, `fuse_teardown`, `fuse_loop`, `fuse_loop_mt`, `fuse_main_real`.
- `fuse_session_exit` unmounts the attached Dokan mount.

Important behavior:
- Dokan DLL loading is deferred until the main loop to avoid Cygwin fork/daemonization issues.
- `fuse_interrupted` is a stub returning `0`.
- `FuseSetAllocationSize` truncates EOF only when requested allocation size is less than current file size; otherwise it succeeds without allocating.
- `fuse_exit` unmounts to force `DokanMain` loop termination.
