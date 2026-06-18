# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsBlackList.hh

## Purpose
Declares `XrdCmsBlackList`, an `XrdJob` that periodically reloads blacklist/whitelist configuration and answers host-present queries with optional redirect payloads.

## Important APIs, Types, and Functions
Public API is `DoIt()`, static `Init()`, and static `Present()`. Private helpers parse blacklist and redirect records and flatten redirect target lists. The documented `Present()` return values distinguish deny, allow, redirect size, and insufficient redirect buffer.

## Control Flow
The scheduler invokes `DoIt()` after `Init()` schedules the job. Runtime callers use `Present()` to query the current parsed list.

## State and Persistence Behavior
The header exposes no instance fields; implementation state is file-scope/global. It depends on an external list file for durable configuration.

## Dependencies and Integration Points
Includes `XrdJob.hh` and forward-declares cluster, scheduler, and list types. Used by CMS cluster admission/selection code.

## Risks and Edge Cases
Because most state is static, initialization order and test isolation matter. Callers must honor the redirect-buffer return convention to avoid dropping redirect data.

## Test Signals
Header-level tests should verify job inheritance and API compatibility with scheduler and cluster code. Behavior tests should focus on `Init()`/`Present()` combinations.
