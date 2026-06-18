# sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_cfg.cpp

## Purpose
`fuse_cfg.cpp` defines the global `fuse_cfg` instance and implements small accessors for configuration values that need validation or synchronized log-file state.

## Important APIs, Types, and Functions
`fuse_cfg_t::valid_uid`, `valid_gid`, and `valid_umask` compare configured values against invalid sentinels from `fuse_cfg.hpp`. `log_file()` and `log_file(std::shared_ptr<FILE>)` read/write the active log file under `_log_mutex`. `log_filepath()` and `log_filepath(const std::string&)` similarly manage a shared string path.

## Control Flow
Configuration is read directly by the rest of libfuse and mergerfs. This implementation only guards log metadata: readers take a shared lock and writers take a unique lock. The filepath setter allocates a new shared string before acquiring the mutex, then atomically swaps the pointer while locked.

## State and Persistence
The only state in this file is the process-global `fuse_cfg` object and its shared pointers. Values are not persisted here; they are populated by mergerfs startup/config parsing elsewhere. The log file pointer and path are reference-counted so readers can hold stable objects after the lock is released.

## Dependencies and Integration Points
The file includes `fuse_cfg.hpp` and uses `<mutex>` plus the shared mutex declared in the header. Consumers include `fuse.cpp`, `fuse_loop.cpp`, `fuse_lowlevel.cpp`, debug logging, and helper code that applies uid/gid/umask, FUSE init caps, thread counts, and log paths.

## Risks
The global object is mutable and used broadly, so initialization order matters. The FILE pointer itself is not made thread-safe by the shared pointer; callers still need to coordinate writes at the logging layer. Changes to invalid sentinel values must stay consistent with the validation methods.

## Test Signals
Check default invalid uid/gid/umask behavior, setting explicit uid/gid/umask, concurrent log path/file readers while replacing the path/file, and startup paths where no log file is configured.
