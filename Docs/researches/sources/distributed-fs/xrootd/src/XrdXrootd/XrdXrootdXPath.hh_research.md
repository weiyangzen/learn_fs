# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdXPath.hh

## Purpose

`sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdXPath.hh` implements a small ordered path-prefix rule list for XRootD path validation and routing options. Protocol handlers use it to decide whether a normalized path is allowed, whether locking, CGI, slash, or multi-write checks should be bypassed, and which static redirect route applies. The source was read as a complete 102-line file.

## Important APIs, Types, and Functions

The exported class is `XrdXrootdXPath`. `Next()`, `Opts()`, and `Path()` expose list navigation and current rule data. `Set()` replaces options and optionally replaces owned path storage. `Insert()` allocates and inserts a new rule in path-length order, using one order for special option-bearing routes and another for ordinary rules. `Validate()` checks whether a candidate path starts with the first matching stored prefix and returns its option bits. Public flags include `XROOTDXP_OK`, `XROOTDXP_NOLK`, `XROOTDXP_NOCGI`, `XROOTDXP_NOSLASH`, and `XROOTDXP_NOMWCHK`.

## Control Flow

The list head is typically a sentinel. `Insert()` walks from `next` and orders longer or shorter prefixes depending on the rule's option bits, then links the new node into the singly linked list. `Validate()` computes or receives a path length, scans while the candidate is at least as long as the stored prefix, and returns the first prefix whose bytes match. XRootD request handlers call `XPList.Validate()`, `RPList.Validate()`, and `RQList.Validate()` after `rpCheck()`/`Squash()` normalization.

## State and Persistence Behavior

Each node owns a `strdup()`-allocated `path` freed by the destructor. There is no destructor recursion, so destroying a sentinel does not free the linked list unless callers walk it elsewhere. Rule state is process configuration state and is read by connection threads without local locking in this class.

## Dependencies and Integration Points

The header uses `<strings.h>` and `<cstdlib>` for C string and allocation APIs. It is integrated by `XrdXrootdXeq.cc` for path policy, static routing lists, no-lock local paths, no-CGI handling, no-leading-slash policy, and multi-write support flags.

## Risks and Edge Cases

The class manually owns C strings and linked nodes, so leaks are possible if list lifecycle is not handled by the owner. `Set()` calls `strlen()`/`strdup()` without null checks beyond `pathdata`, and `Insert()` does not handle allocation failure. Prefix validation is byte-prefix based and does not enforce path-component boundaries, so configuration must avoid ambiguous prefixes such as `/a` matching `/abc` unless that is intentional. Concurrent mutation after startup would be unsafe.

## Test Signals

Tests should cover rule ordering for ordinary and option-bearing paths, exact and prefix matches, nonmatches, empty sentinel paths, path lengths passed explicitly to `Validate()`, `XROOTDXP_NOSLASH` behavior through callers, and ambiguous prefixes. Static redirect and no-lock/multi-write integration tests provide higher-level coverage.
