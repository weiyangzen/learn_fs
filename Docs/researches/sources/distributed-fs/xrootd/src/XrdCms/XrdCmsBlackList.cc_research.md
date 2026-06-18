# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsBlackList.cc

## Purpose
Implements dynamic CMS blacklist/whitelist loading, matching, logging, and optional redirect target generation for cluster host admission decisions.

## Important APIs, Types, and Functions
Local `BL_Grip` manages temporary linked lists. `BL_Info` packs exact/wildcard/redirect metadata into an `XrdOucTList` value. Main methods are `AddBL()`, `AddRD()` overloads, `DoIt()`, `Flatten()`, `GetBL()`, `Init()`, `Present()`, and `MidNightTask::Ring()`.

## Control Flow
`Init()` chooses blacklist vs whitelist mode, resolves the file path, reads an initial file if present, schedules periodic `DoIt()`, and registers midnight logging. `DoIt()` stats the file, reloads on modification/removal, atomically swaps global lists under `blMutex`, updates the cluster, frees old lists, and reschedules itself. `Present()` scans exact or wildcard entries and returns allow/deny/redirect status.

## State and Persistence Behavior
Global state stores scheduler/cluster pointers, current real list, redirect vector, config filename, modification time, check interval, redirect count, and whitelist mode. Persistence is the external blacklist/whitelist file; the process holds parsed in-memory lists.

## Dependencies and Integration Points
Depends on scheduler jobs, CMS cluster update hooks, network address normalization, token/list/stream utilities, config environment, logger midnight tasks, and manager parsing utilities.

## Risks and Edge Cases
Wildcard matching uses one `*` with prefix/suffix lengths and may surprise users expecting glob semantics. Redirect data is flattened into a bounded 4096-byte buffer and truncated silently once full. `AddRD(XrdOucTList **, ...)` is declared `bool` but returns `-1` on errors, which converts to `true`; this is suspicious. Global mode/state make multiple independent blacklist instances impractical.

## Test Signals
Tests should parse exact names, wildcard names, IPv6 redirect specs, missing ports, too many redirects, file removal, reload failures, whitelist inversion, redirect buffer sizing, midnight logging, and `Present()` return conventions.
