<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdmin.hh -->
# sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdmin.hh

## Purpose
`XrdFrmAdmin.hh` declares the `XrdFrmAdmin` command processor used by `frm_admin`. It is the central interface joining command dispatch, audit/find/query/remove/reloc helpers, option state, counters, checksum state, and transfer queue proxy state.

## Important APIs And Types
Public methods are the command entry points and argument setters. Private methods are grouped by feature: audit name/space/usage helpers, checksum listing/printing, find variants, parsing helpers, mark/mmap/pin/lock helpers, query variants, relocation helpers, unlink helpers, and verification helpers. Static help strings provide per-command usage text. The nested `Opt` struct stores command-local flags, target arguments, UID/GID, and keep-time details.

## Control Flow And State
The object is long-lived across interactive commands. `Parse()` clears `Opt` for each command, but counters and `finalRC` are explicitly managed by command implementations. `ArgV/ArgC` and `ArgS` allow the same parser to support command-line and interactive modes. `frmProxy`/`frmProxz` cache queue proxy initialization.

## Dependencies And Integration Points
The header depends on checksum data and namespace walking. It forward-declares proxy, fileset, args, and list types. `XrdFrm::Admin` is declared as a namespace-global singleton and defined in `XrdFrmAdminMain.cc`.

## Risks And Test Signals
The class is broad and stateful, so command implementations can accidentally rely on stale counters or flags if parsing paths are bypassed. The `Opt.Args[2]` fixed capacity shapes parser usage and can be a source of mistakes. Tests should exercise multiple interactive commands in one process to catch stale state, verify global singleton initialization order, and build-check that all private methods declared here are defined in the linked admin target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdmin.hh -->
