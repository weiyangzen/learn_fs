# sources/test-tools/syzkaller/tools/syz-trace2syz/proggen/return_cache.go

## Purpose

`return_cache.go` implements the resource-return cache used during trace conversion. It lets later syscall arguments reference earlier returned resources instead of hard-coding raw numeric values.

## Important APIs, Types, and Functions

The main type is `returnCache map[string]prog.Arg`. Functions are `newRCache`, `returnCacheKey`, `returnCache.cache`, and `returnCache.get`. Keys combine the first resource kind from `prog.ResourceType.Desc.Kind` with the parser IR string representation.

## Control Flow

When `genResult` or an out resource argument sees a returned resource, it calls `cache`. When `genResource` handles an input constant, it calls `get`; a hit creates a `prog.ResultArg` linked to the original result, while a miss falls back to a raw value.

## State and Persistence Behavior

The cache is per-generated program through `context.returnCache`. It is an in-memory map with no eviction because traces are processed once and then discarded.

## Dependencies and Integration Points

It depends on `prog.ResourceType`, `prog.Arg`, and parser IR stringification. It is coupled to `proggen.go` resource generation and result handling.

## Risks and Test Signals

`returnCacheKey` fatals on non-resource types and assumes `Desc.Kind` is non-empty. String-based keys can collide if distinct parser IR values stringify identically in a relevant context. Tests in `proggen_test.go` cover file descriptor and pipe/inotify resource reuse; additional stress should cover reused numeric values across different resource kinds.
