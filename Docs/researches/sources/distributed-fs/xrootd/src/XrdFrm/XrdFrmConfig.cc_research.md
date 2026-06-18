<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmConfig.cc -->
# sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmConfig.cc

## Purpose
`XrdFrmConfig.cc` implements configuration for FRM admin, purge, and transfer subsystems. It parses command-line options and config-file directives, sets environment/logging, loads OSS/xattr/checksum/name mapping plugins, builds admin/queue paths, configures spaces and policies, and initializes subsystem-specific runtime support.

## Important Functions
`Configure()` is the main orchestration entry. It parses options, sets `XRDINSTANCE`, `XRDHOST`, `XRDPROG`, and `XRDNAME`, configures logging/background mode, reads the config file through `ConfigProc()`, creates admin paths with `ConfigPaths()`, loads plugins through `XrdOfsConfigPI`, and dispatches to admin/purge/xfr setup. Public path helpers `LocalPath`, `LogicalPath`, and `RemotePath` wrap name2name plugins or identity mapping. `Space()` looks up configured space directories. `Stat()` chooses `StatPF` when supported. Directive handlers include `xapath`, `xcks`, `xcnsd`, `xcopy`, `xcmax`, `xdpol`, `xmon`, `xnml`, `xpol`, `xpolprog`, `xqchk`, `xsit`, `xspace`, and `xxfr`.

## Control Flow, State, And Persistence
The constructor establishes defaults for timing, queue limits, admin mode, lock names, policy, transfer commands, and subsystem identity. Config parsing mutates many persistent process fields: paths, plugin pointers, space lists, policies, transfer command templates, monitoring destinations, CNS mode, fail-file directory, and usage behavior. `ConfigPF()` writes pid files; `ConfigPaths()` creates admin directories and STOPPURGE path; `ConfigMum()` temporarily captures stderr during admin/no-log initialization.

## Dependencies And Integration Points
The implementation is deeply integrated with XRootD: `XrdOfsConfigPI`, `XrdOss`, `XrdOssSpace`, `XrdOucN2NLoader`, `XrdOucStream`, `XrdOucMsubs`, `XrdFrmCns`, `XrdFrmMonitor`, `XrdNetCmsNotify`, and global OSS export path lists. Admin commands rely on `Config` for all path, space, checksum, OSS, CMS, and queue decisions; transfer and purge daemons use the same object with different `SubSys` mode.

## Risks And Test Signals
This file is configuration-critical and uses many fixed buffers plus string mutation. `Grab()` contains `if (*Dest) {free(*Dest); Dest = 0;}` which nulls the local pointer variable rather than `*Dest`, though it later assigns `*Dest`; this is harmless for assignment but leaves a confusing pattern. `xspace()` no longer supports old non-XA spaces and returns an error for `oss.cache` without `xa`. `ConfigXeq()` ignores unknown prefixed directives with warnings but suppresses unprefixed unknowns. Tests should cover each subsystem mode, missing config, every directive parser, invalid values, plugin-load failures, background logging handoff, admin path creation, CNS modes, space wildcard expansion, policy defaults/overrides, name2name mapping, and transfer command option combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmConfig.cc -->
