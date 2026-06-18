# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClientConfig.cc

## Purpose
Implements CMS client configuration parsing for managers, supervisors, and servers, including admin socket paths, manager lists, request timing, tracing, VNID/system ID setup, and performance monitor plugin loading.

## Important APIs, Types, and Functions
Implements destructor cleanup, `Configure()`, `ConfigProc()`, `ConfigSID()`, `ConfigXeq()`, and directive parsers `xapath()`, `xcidt()`, `xconw()`, `xmang()`, `xperf()`, `xreqs()`, `xtrac()`, and `xvnid()`.

## Control Flow
`Configure()` seeds environment-derived defaults, parses the config file, validates required manager/proxy manager lists, exports local CMS path variables, computes role-specific socket paths, initializes the message pool, and optionally loads a performance monitor. `ConfigProc()` scans `cms.`, `odc.`, and compatibility directives. `xmang()` handles role modifiers, selection modes, ports, conditionals, and manager list parsing.

## State and Persistence Behavior
The object owns heap strings for paths, VNID/perf plugin data, cluster ID tag, and linked manager/proxy lists. It exports `XRDCMSPATH`, `XRDOLBPATH`, and `XRDCMSMAN` into the process environment. No config file is written.

## Dependencies and Integration Points
Depends on CMS message/security/perf/trace/utils, Ouc config streams, environment utilities, time/int parsing, and dynamic plugin loading. Integrates with `XrdCmsClientMsg::Init()` and `XrdCmsSecurity` system ID/VNID helpers.

## Risks and Edge Cases
Directive parsing is token-order sensitive and keeps many compatibility aliases. `ConfigProc()` passes `var+4` even for `all.manager`, which relies on prefix shape. Performance monitor loading only happens when both `prfLib` and `cmsMon` are set. Environment exports affect later components globally.

## Test Signals
Tests should parse adminpath, cidtag length, conwait, manager modes/ports/conditionals, request options, trace flags including negation, VNID forms, perf plugin options, missing manager errors, supervisor path rewrites, and environment exports.
