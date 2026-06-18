<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdmin.cc -->
# sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdmin.cc

## Purpose
`XrdFrmAdmin.cc` implements the main `frm_admin` command dispatcher and shared command helpers. It handles top-level admin verbs, parses common options, manages final return status, initializes transfer queue proxy access, and delegates heavy filesystem operations to companion files.

## Important Functions
Top-level commands include `Audit`, `Chksum`, `Find`, `Help`, `MakeLF`, `Mark`, `Mmap`, `Mv`, `Pin`, `Query`, `Reloc`, and `Remove`. `xeqArgs()` maps abbreviated command names to methods. `Parse()` resets `Opt`, wires either argv-array or interactive-string arguments into `XrdOucArgs`, decodes common option letters, and collects required positional arguments. `ParseKeep()`, `ParseOwner()`, `ParseSpace()`, and `ParseType()` implement shared value parsing. `ConfigProxy()` discovers existing transfer queue files and initializes `XrdFrcProxy` for `query xfrq`. `VerifyAll()` recognizes `/*` directory-wide syntax, and `VerifyMP()` checks OSS export flags before migratable/purgeable operations.

## Control Flow, State, And Persistence
`frm_admin` state lives in the singleton `XrdFrm::Admin`. Each command mutates `Opt`, counters such as `numFiles`, and `finalRC`. Filesystem persistence happens indirectly through checksum manager calls, OSS rename/reloc/unlink, xattrs, lock files, queue proxy access, and audit repair helpers. `Quit()` exits with `finalRC`.

## Dependencies And Integration Points
This file depends on `XrdFrmConfig` for path mapping, OSS access, checksum manager, queue path, instance name, and export metadata. It integrates with `XrdFrcProxy`, `XrdFrcUtils`, `XrdOucArgs`, NSS user/group lookups, and the companion admin implementation files declared in `XrdFrmAdmin.hh`.

## Risks And Test Signals
`Mmap()` calls `Parse("pin ", ...)`, so mmap parse diagnostics can incorrectly name `pin`. `Parse()` supports only two `Opt.Args` slots; commands that need more must pull additional args manually. `ParseKeep()` uses `%D`, which is locale/century-sensitive, and does not null-check `strptime()` before dereferencing `eP`. `ConfigProxy()` uses fixed buffers and queue file existence as capability discovery. Tests should cover every command abbreviation, interactive and argv modes, invalid user/group/time/checksum input, forced and prompted migratable/purgeable decisions, and queue listings with missing and present queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdmin.cc -->
