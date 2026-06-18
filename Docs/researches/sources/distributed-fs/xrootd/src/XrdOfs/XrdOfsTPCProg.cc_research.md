# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPCProg.cc

## Purpose

`XrdOfsTPCProg.cc` implements the bounded pool of external transfer-program runners for OFS TPC jobs. It prepares command arguments/environment, writes temporary delegated-credential files, drains transfer output, reports monitoring data, and returns workers to the idle pool.

## Important APIs, Types, and Functions

Implemented methods are constructor, `ExportCreds`, `Init`, `Run`, `Start`, and `Xeq`. Static state is `pgmMutex` and idle stack `pgmIdle`. Local RAII class `credFile` builds unique credential-file paths and unlinks them on destruction. Thread entry `XrdOfsTPCProgRun` calls `Run()`.

## Control Flow

`Init()` allocates `Cfg.xfrMax` `XrdOfsTPCProg` objects and calls `XrdOucProg::Setup` with `Cfg.XfrProg`. `Start()` pops an idle runner, attaches a job, and starts a thread. `Run()` loops while each completed job hands it another queued job. For each job it calls `Xeq()`, fills monitor timing/URL/client/size data if configured, invokes `Job->Done()`, and finally pushes itself back onto the idle list. `Xeq()` writes credentials if needed, builds `-C` checksum and `-S` stream arguments, exports `XRD_TIDENT`, optional source/target protocol variables, optional `XRD_CPTARGET`, and optional credential env var, starts the external program, drains lines to capture failure text and IPv4 marker, gets the exit code, logs/removes on failure, and marks success on success.

## State and Persistence Behavior

Runners are long-lived heap objects recycled through an idle stack. Threads are per active transfer. Temporary credential files are mode `0600`, named under the configured credential path using origin plus sequence, and unlinked by `credFile`. Transfer success/failure is written back into the job and optional monitor, not persisted elsewhere.

## Dependencies and Integration Points

The file uses `XrdOucProg` and `XrdOucStream` for external process execution, `XrdSysThread`, `XrdSysFD`, `XrdNetIdentity`, `XrdXrootdTpcMon`, `XrdOss` for stat/unlink, and OFS trace/error globals. It is the runtime boundary to `xrdcp --server` or any configured transfer program.

## Risks and Edge Cases

Credential filenames include origin text; any unexpected characters must be tolerated by the filesystem and security policy. The failure-message parser records text after `": "`, so transfer-program output format changes affect user errors. `Start()` leaves the runner attached if thread creation fails until caller handles `rc`; this path needs regression coverage. Monitoring temporarily edits query delimiters in job strings and restores them, so null/malformed strings are important edge cases.

## Test Signals

Tests should cover pool sizing, no-idle queuing, thread creation failure, command argument construction, credential export/unlink, checksum and stream options, reproxy environment, transfer stdout parsing, nonzero exit cleanup, monitor reporting, and cancellation via `JobStream.Drain()`.
