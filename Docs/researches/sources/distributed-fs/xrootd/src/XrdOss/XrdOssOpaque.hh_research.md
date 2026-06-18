# sources/distributed-fs/xrootd/src/XrdOss/XrdOssOpaque.hh

## Purpose
Defines opaque environment keys and constants used to pass OSS-specific allocation and staging hints through `XrdOucEnv`.

## Important APIs, types, and functions
`OSS_ASIZE` names the estimated allocation size key. `OSS_CGROUP` names the requested cache group or `group:path` constraint. `OSS_USRPRTY` and `OSS_SYSPRTY` carry user/system staging priority keys. `OSS_CGROUP_DEFAULT` is `"public"`. `OSS_VARLEN` caps variable length, `OSS_MAX_PRTY` caps priorities, and `OSS_USE_PRTY` is the default priority.

## Control flow
No executable flow. Runtime create/stage paths read these keys from env objects to influence allocation and queueing.

## State and persistence
No mutable state. The macros cast string literals to `char *`, matching older APIs that expect mutable `char *` names.

## Dependencies and integration points
Used by `XrdOssCreate.cc`, `XrdOssCache.cc`, staging/transfer code, and callers that set opaque URL/env parameters. `OSS_CGROUP_DEFAULT` must match the public group logic in `XrdOssCache_Group`.

## Risks and test signals
Because keys are macros rather than typed constants, typo resistance is low. Tests should cover `oss.asize`, `oss.cgroup`, default group fallback, priority bounds, and interaction with URL-decoded colocation parameters.
