# sources/storage-engines/foundationdb/fdbcli/AdvanceVersionCommand.cpp

## Purpose

`AdvanceVersionCommand.cpp` implements the `fdbcli advanceversion <VERSION>` command. It forces a cluster to advance to at least the supplied commit version through the special key space, primarily for forced recovery or version-floor management.

## Important APIs, Types, and Functions

The command defines `advanceVersionSpecialKey` as `\xff\xff/management/min_required_commit_version`. `advanceVersionCommandActor` parses the target version, creates transactions, enables special-key-space writes, reads the current read version, writes the requested version when the current version is not yet above it, commits, and retries until the read version has advanced. `advanceVersionFactory` registers command help.

## Control Flow

The actor requires exactly two tokens. It parses the second token with `sscanf` and `%n` to reject trailing garbage. In a retry loop, it sets `SPECIAL_KEY_SPACE_ENABLE_WRITES`, gets a read version, writes the minimum required commit version if `rv <= v`, commits, and loops again. Once the observed read version is greater than the requested version, it prints the current read version and returns success. Errors are handled through `tr->onError`.

## State and Persistence Behavior

The command writes to a management special key, causing the cluster to recover or move forward to satisfy the minimum required commit version. It does not directly write ordinary key-value data, but the side effect is cluster-wide and operationally significant.

## Dependencies and Integration Points

It uses `fdbcli/fdbcli.h`, `IClientApi`, Flow arena/ref helpers, `safeThreadFutureToFuture`, `boost::lexical_cast`, and `fmt`. It runs inside the fdbcli command factory framework and relies on special-key-space semantics implemented below the client API.

## Risks and Edge Cases

The command loops after commit until a subsequent read version proves the cluster is past the target, so very large requested versions can have operational impact. It accepts signed `Version` syntax; negative or nonsensical operational values are not explicitly rejected in this file. Because it writes special keys, missing transaction option setup would fail. Retrying through `onError` is standard but may repeat the special-key write.

## Test Signals

No direct test from this subset targets `advanceversion`. Basic command testing would need to verify argument count, invalid version parse rejection, special-key write permissions, retry behavior, and final printed read version.
