# sources/security-integrity/selinux/checkpolicy/parse_util.h

## Purpose

`parse_util.h` declares the shared source-policy parsing entry point for checkpolicy-related tools. It documents that callers must provide an already created and configured `policydb_t`, and that this helper only parses source into the policydb without running assertion, hierarchy, or other post-parse validation.

## Important API

`int read_source_policy(policydb_t *p, const char *file, const char *progname);`

`p` is the destination policydb, `file` is the source policy path, and `progname` is used in diagnostics. The return contract is `0` for success and `-1` for parse/setup failure.

## Control Flow and Integration

The header is consumed by tools that need the same two-pass parser behavior. It includes `<sepol/policydb/policydb.h>` so callers have `policydb_t`. The implementation wires into flex/yacc globals, `queue.c`, `policy_define.c`, and `policy_scan.l`.

## State, Dependencies, and Risks

The header itself is stateless. Its most important design signal is the comment that the policydb must already be configured. If a caller does not set policy type, target platform, or MLS mode correctly before calling, grammar actions can reject valid constructs or build the wrong object context tables.

## Test Signals

API-level tests should instantiate a policydb, set required policy properties, call `read_source_policy()`, and verify both success output and parser error handling for malformed source.
