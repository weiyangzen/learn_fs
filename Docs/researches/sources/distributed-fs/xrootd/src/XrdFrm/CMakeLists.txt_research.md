<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdFrm/CMakeLists.txt

## Purpose
`XrdFrm/CMakeLists.txt` defines the build targets for the File Residency Manager library and command-line daemons. It collects common FRM implementation into a static `XrdFrm` library and builds `frm_admin`, `frm_purged`, `frm_xfrd`, and `frm_xfragent`.

## Important Targets
`XrdFrm` includes configuration, file walking, monitoring, sorting, CNS notifications, migration, request boss, transfer, transfer daemon, job, and queue sources. `frm_admin` is built from admin audit, core, files, find, main, query, and unlink sources plus the static library. `frm_purged` builds purge sources. `frm_xfrd` and `frm_xfragent` both compile `XrdFrmXfrMain.cc` and link the common library.

## Dependencies And Integration Points
All executables link `XrdFrm`, `XrdServer`, `XrdUtils`, thread libraries, extra/socket libraries, and for `frm_admin`, readline/ncurses support. If readline is present, its include directory is added privately to `frm_admin`. Install rules place all executables under `${CMAKE_INSTALL_BINDIR}`.

## Control Flow And State
This is declarative build state. The static library concentrates shared FRM behavior, while command-specific translation units provide process entry points and admin command surfaces.

## Risks And Test Signals
The listed source set for `frm_admin` does not include `XrdFrmAdminReloc.cc`, even though that file is in this subset and defines the private `XrdFrmAdmin::Reloc(char*, char*)` relocation implementation. The public `Reloc()` in `XrdFrmAdmin.cc` currently calls `Config.ossFS->Reloc()` directly, so the missing source may be dead or stale, but this deserves build-symbol and behavior verification. Tests should include clean builds with and without readline, checking that every declared admin method has a linked definition and that install rules include all expected tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/CMakeLists.txt -->
