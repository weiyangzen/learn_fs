<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/data_blob.c -->
# sources/user-network-fs/cifs-utils/data_blob.c

## Purpose

`data_blob.c` implements Samba-style arbitrary byte blob helpers used by ASN.1, SPNEGO, and Kerberos upcall code.

## Important APIs, Types, and Functions

It defines `data_blob_null`, `data_blob_named`, `data_blob_talloc_named`, and `data_blob_free`.

## Control Flow

`data_blob_named` returns a zeroed blob for `(NULL, 0)`, duplicates provided data with `talloc_memdup`, or allocates an uninitialized byte array with `talloc_array` when only a length is supplied. `data_blob_talloc_named` creates a blob and steals the allocation into a supplied context. `data_blob_free` talloc-frees the payload and resets pointer and length.

## State and Persistence Behavior

Blob state is heap/talloc memory owned by the caller. There is no global mutable state except the constant null blob.

## Dependencies and Integration Points

It depends on talloc through `data_blob.h` and is used by ASN.1/OID encoding, SPNEGO wrapping, and Kerberos ticket/session-key transport.

## Risks and Edge Cases

Callers must free blobs exactly once and respect that `data_blob_named` copies input data. Allocation failure returns `data == NULL` and `length == 0`, which callers must check before use. Sensitive ticket/session-key blobs should be scrubbed by callers if needed; `data_blob_free` does not zero memory first.

## Test Signals

Unit tests should cover null blobs, copied input independence, uninitialized allocation length, talloc parent stealing, and double-free-safe caller patterns.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/data_blob.c -->
