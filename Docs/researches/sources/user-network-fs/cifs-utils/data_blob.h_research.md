<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/data_blob.h -->
# sources/user-network-fs/cifs-utils/data_blob.h

## Purpose

`data_blob.h` declares the `DATA_BLOB` byte-buffer type and allocation/free helpers.

## Important APIs, Types, and Functions

The header defines `typedef struct datablob { uint8_t *data; size_t length; } DATA_BLOB`, `struct data_blob_list_item`, macro alias `ldb_val`, convenience macros `data_blob`, `data_blob_talloc`, `data_blob_dup_talloc`, function declarations, and `data_blob_null`.

## Control Flow

Callers construct blobs with the macros or named functions and release them with `data_blob_free`.

## State and Persistence Behavior

The header defines caller-owned talloc-backed memory conventions. It does not persist state.

## Dependencies and Integration Points

It depends on `talloc.h` and `stdint.h`, and it is shared by ASN.1, CLDAP, SPNEGO, and upcall code.

## Risks and Edge Cases

The macros use `__location__`, a talloc/Samba convention that must be available from included headers. The ABI comment implies signature changes may require shared-library version consideration in upstream contexts.

## Test Signals

Compile tests should verify macro expansion under the project compiler flags, and blob allocation tests should include parent contexts and duplication.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/data_blob.h -->
