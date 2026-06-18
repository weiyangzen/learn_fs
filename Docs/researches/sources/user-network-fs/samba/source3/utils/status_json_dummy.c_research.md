# sources/user-network-fs/samba/source3/utils/status_json_dummy.c

## Purpose

`sources/user-network-fs/samba/source3/utils/status_json_dummy.c` provides no-op implementations of the `status_json.h` interface when Samba is built without Jansson JSON support. The source was read as a complete 111-line file.

## Important APIs, Types, and Functions

It defines every JSON interface function: `add_section_to_json`, `add_general_information_to_json`, profile item helpers, connection/session traversal JSON hooks, share-mode and byte-range-lock JSON printers, and `print_notify_rec_json`.

## Control Flow

Every function immediately returns success-like values (`0` for integer functions and `0`/false for the bool notify function). In normal non-Jansson runtime, `status.c` rejects `--json` before these emitters are used, so the dummy module mainly satisfies link-time references.

## State and Persistence Behavior

No state is read or written. Parameters are ignored, and no JSON tree exists in `struct traverse_state` for non-Jansson builds.

## Dependencies and Integration Points

The file includes the same broad Samba status/open-file/security headers needed for signature compatibility. `wscript_build` chooses this file instead of `status_json.c` when `HAVE_JANSSON` is not configured.

## Risks and Edge Cases

If future code calls JSON emitters without first rejecting JSON mode in non-Jansson builds, these no-ops could make the command appear to succeed while emitting no structured content. Signature drift against the real implementation would cause build failures.

## Test Signals

Build tests without Jansson should link `smbstatus`, and runtime tests should verify `smbstatus --json` reports JSON support unavailable rather than silently producing empty output.
