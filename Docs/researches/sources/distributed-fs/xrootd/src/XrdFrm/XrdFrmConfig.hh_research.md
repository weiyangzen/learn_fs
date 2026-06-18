<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmConfig.hh -->
# sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmConfig.hh

## Purpose
`XrdFrmConfig.hh` declares the configuration object shared by FRM admin, purge, migration, prestage, and transfer subsystems. It is the main runtime state container for paths, plugins, policies, transfer commands, spaces, timing knobs, and subsystem identity.

## Important APIs And Types
Public fields expose program identity, admin paths, queue paths, PID paths, MSS and transfer command state, plugin pointers, UID/GID, timing values, feature flags, path/space lists, and purge policy state. `Cmd` describes configured copy commands and option flags such as allocation, `$MDP`, stats, monitoring data, and remove-on-error. `VPInfo` stores named virtual spaces and directories. `Policy` stores free-space thresholds, hold time, external-policy flag, and space name. Public methods include `Configure`, path mapping, CTA/export checks, space lookup, and stat abstraction. `SubSys` selects admin, migrate, prestage, purge, or transfer behavior.

## Control Flow And State
`XrdFrmConfig` is stateful and generally used as the global `XrdFrm::Config`. Constructor defaults are completed by `Configure()`. Many fields are read directly by admin and daemon code rather than through accessors, so invariants are enforced mostly by configuration sequencing.

## Dependencies And Integration Points
The header depends on `XrdOssSpace.hh` and forward-declares XRootD plugin, logging, stream, name mapping, checksum, and list types. It declares private directive parsers implemented in `XrdFrmConfig.cc`. Every file in this subset that needs path mapping, OSS access, checksum support, queue paths, or space lists depends on this object.

## Risks And Test Signals
The broad public field surface makes it easy for later code to observe partially initialized state or mutate fields inconsistently. Ownership is mixed: many `char*` fields are allocated with `strdup()` and freed/replaced in parsers, while destructors intentionally do little. Tests should validate default constructor state, full `Configure()` transitions for each subsystem, null-pointer behavior when optional plugins are absent, and that direct consumers behave correctly after failed configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmConfig.hh -->
