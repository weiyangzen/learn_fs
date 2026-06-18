# sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/layout.rs

Purpose: Defines the on-disk/in-blob binary layout for fsblob headers.

Important APIs/types/functions: constants map blob type magic bytes and `FORMAT_VERSION_HEADER`. `BlobType` implements `binary_layout::LayoutAs<u8>`. `binary_layout!` declares `fsblob_header` with version, blob type, and parent id, plus `fsblob` as header plus variable data.

Control flow: `try_read` rejects unknown blob type magic values; `try_write` maps enum variants to bytes. Other modules use generated views to read/write header fields.

State and persistence behavior: this is the compatibility contract for every typed blob. Version is currently `1`; parent is persisted as raw `BLOBID_LEN` bytes.

Dependencies and integration points: used by `BaseBlob` for all parsing/creation and by typed blob wrappers through `BlobType`.

Risks: comments note parent pointers are not validated when traversing. Any layout change requires a format-version migration path. `BlobType` is distinct from `EntryType`, so duplicated type mapping must stay synchronized.

Test signals: tests should assert exact header size/field offsets, invalid magic rejection, and round-trip creation/parsing for each blob type.
