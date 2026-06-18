# sources/distributed-fs/xrootd/src/XrdOss/XrdOssSIgpfsT.cc

## Purpose
Provides a stat-info plugin for GPFS backed by tape, allowing stat calls to hide offline/nonresident files or report them depending on configured program/role-specific parameters.

## Important APIs, types, and functions
The exported global `XrdOssStatInfoResOnly` stores the errno policy for nonresident files, defaulting to `ENOENT`. `XrdOssStatInfo()` performs `stat()`, treats size-zero or allocated-block files as online, and for nonresident files either returns `ENOENT` when `XRDOSS_resonly` is requested, returns the configured errno, or succeeds when all files are allowed. `XrdOssStatInfoParm()` parses `all`, `online`, and `online:eperm`. `XrdOssStatInfoInit()` reads parameters from `XrdOucEnv`, applying increasingly specific keys `stat`, `stat.<prog>`, and `stat.<prog>.<role>`, normalizes legacy role names, logs the effective policy, and returns the stat hook. `XrdVERSIONINFO` publishes plugin version metadata.

## Control flow
Initialization evaluates global, program-specific, then role-specific settings so later matches override earlier policy. Runtime stat calls are simple: real stat, online heuristic, policy-based errno assignment.

## State and persistence
Only process-global policy state is persisted in memory. No disk writes occur.

## Dependencies and integration points
Loaded by `oss.statlib` through `XrdOssConfig.cc`. Uses `XRDPROG` and `XRDROLE` environment variables, `XrdOucEnv` parsing, and the `XrdOssStatInfo` plugin ABI.

## Risks and test signals
The online heuristic relies on `st_blocks`, which is filesystem-specific. Tests should cover all parameter scopes and override order, invalid parameter rejection, role normalization, `XRDOSS_resonly`, zero-size files, sparse/offline files, and both `ENOENT`/`EPERM` policies.
