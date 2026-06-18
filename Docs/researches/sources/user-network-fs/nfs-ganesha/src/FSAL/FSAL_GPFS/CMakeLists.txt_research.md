# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/CMakeLists.txt

Purpose: this build file defines the GPFS FSAL module target. It adds GPFS FSAL include paths, optionally includes DBus headers, enumerates all GPFS FSAL source files, creates the `fsalgpfs` loadable module, applies sanitizer instrumentation, links against Ganesha and system libraries, sets the module version, and installs it into the FSAL destination.

Important build APIs and targets: `fsalgpfs_LIB_SRCS` includes module registration, export, handle, file I/O, upcall, DS/MDS pNFS, unlink, symlink, rename, create, fileop, attrs, lock, lookup, convert, internal open-handle wrappers, GPFS extensions, and stats sources. `add_library(fsalgpfs MODULE ...)` builds a plugin-style shared object. `target_link_libraries()` links `ganesha_nfsd`, `${SYSTEM_LIBRARIES}`, and `${LDFLAG_DISALLOW_UNDEF}`. `set_target_properties()` declares version `4.2.0` and soversion `4`.

Control flow: CMake evaluates DBus include handling first, then module include directories, source collection, target creation, sanitizer attachment, link rule setup, version metadata, and install rule.

State and persistence: this file persists no runtime state, but it controls which source files are compiled into the GPFS FSAL. Omitting a file here removes operation implementations from the module.

Dependencies and integration: it integrates with the repository's CMake variables, sanitizer helper, Ganesha core target, and FSAL install layout. GPFS-specific headers are included from the FSAL source directory.

Risks and test signals: unresolved symbol policy depends on `${LDFLAG_DISALLOW_UNDEF}`, so platform link behavior matters. Adding new GPFS source files requires updating this list. DBus includes are conditional but no DBus library is linked here, so dependencies must be satisfied elsewhere. Tests are build-oriented: configure with and without `USE_DBUS`, build `fsalgpfs` with sanitizers enabled, verify no undefined symbols, and confirm install destination contains the module.
