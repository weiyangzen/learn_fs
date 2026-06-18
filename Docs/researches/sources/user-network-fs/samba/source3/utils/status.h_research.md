# sources/user-network-fs/samba/source3/utils/status.h

## Purpose

`sources/user-network-fs/samba/source3/utils/status.h` defines the shared status traversal state and crypto classification enum used by `smbstatus`, JSON output, and profile output. The source was read as a complete 45-line file.

## Important APIs, Types, and Functions

The key type is `struct traverse_state`, with `json_output`, `first`, `resolve_uids`, and, under `HAVE_JANSSON`, `root_json`. The key enum is `enum crypto_degree` with `CRYPTO_DEGREE_NONE`, `CRYPTO_DEGREE_PARTIAL`, `CRYPTO_DEGREE_ANONYMOUS`, and `CRYPTO_DEGREE_FULL`.

## Control Flow

This header has no runtime control flow. It supplies the state object passed through `status.c` traversal callbacks and helper emitters.

## State and Persistence Behavior

The state is per-command runtime state. `first` controls text header emission, `json_output` selects JSON versus text emitters, `resolve_uids` controls UID name enrichment for open-file records, and `root_json` owns the top-level Jansson object while `smbstatus` runs.

## Dependencies and Integration Points

When Jansson is available the header includes `<jansson.h>`, `audit_logging.h`, and `auth/common_auth.h` so `struct json_object` is visible. It is included by `status.c`, `status_json.h`, and `status_profile.h`.

## Risks and Edge Cases

Because JSON fields are conditionally compiled, all users must be built with consistent `HAVE_JANSSON` settings. The enum ordering is used as a classification contract between `status.c` and JSON/text formatters.

## Test Signals

Compile tests should cover both Jansson and non-Jansson builds, plus text and JSON traversal paths that rely on the same state object.
