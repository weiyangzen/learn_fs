# Research: sources/user-network-fs/samba/source3/lib/netapi/sid.c

Purpose: implements public SID string conversion helpers compatible with Windows `ConvertSidToStringSid` and `ConvertStringSidToSid` semantics for the `struct domsid` type exposed in `netapi.h`.

Important APIs/functions: `ConvertSidToStringSid` validates inputs, formats a `domsid` through Samba `dom_sid_str_buf`, duplicates the string with `SMB_STRDUP`, and returns boolean success. `ConvertStringSidToSid` parses a SID string with `string_to_sid`, allocates a `struct domsid` with `SMB_MALLOC`, copies the parsed SID, and returns boolean success.

Control flow: both functions return `false` for NULL parameters or allocation/parsing failure. The conversion path casts between public `struct domsid` and Samba internal `struct dom_sid`, relying on compatible layout.

State and persistence: stateless except for heap allocation returned to the caller. The string result is documented in the header as freed with `free(3)`, while parsed SID memory is allocated with Samba allocation macros; callers must use the expected deallocator for their build.

Dependencies/integration: includes public `netapi.h` and Samba security SID helpers. These functions support callers that need to inspect SIDs returned in user/group/localgroup structures or supply SIDs for local group member operations.

Risks: ABI correctness depends on `struct domsid` matching `struct dom_sid`. Allocation ownership is easy to get wrong because these helpers do not use `NetApiBufferFree`. Invalid SID strings fail cleanly, but there is no detailed error code beyond boolean false.

Test signals: tests should round-trip well-known and domain SIDs, reject malformed strings, handle NULL arguments, verify allocation/free behavior under leak tools, and confirm maximum subauthority handling matches `MAXSUBAUTHS`.
