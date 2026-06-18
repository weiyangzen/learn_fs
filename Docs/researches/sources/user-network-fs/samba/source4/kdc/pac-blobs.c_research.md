## sources/user-network-fs/samba/source4/kdc/pac-blobs.c

Purpose: helper for representing PAC buffers as an ordered list plus fast index by supported PAC type. It lets PAC update code replace, add, remove, and validate buffer types while preserving original buffer order where possible.

Important APIs and functions: `pac_blobs_from_krb5_pac()` reads buffer types from a krb5 PAC, initializes type indexes to `SIZE_MAX`, rejects duplicate supported types, and records original order. `_pac_blobs_ensure_exists()` checks required type presence. `_pac_blobs_replace_existing()` attaches a replacement `DATA_BLOB` for an existing type. `pac_blobs_add_blob()` appends or replaces a type when a non-NULL blob is supplied. `pac_blobs_remove_blob()` removes a type, shifts later entries, and updates indexes.

Control flow: unsupported PAC types remain in the ordered array but are not indexed unless within the supported type range. Replacement does not copy blob data; it stores the caller's pointer. Removal leaves blob storage ownership untouched.

State and persistence: in-memory talloc structure only. Used during PAC update before constructing a new krb5 PAC.

Dependencies and integration: used heavily by `pac-glue.c` validation/update paths. Depends on PAC type constants from generated NDR headers and krb5 PAC type enumeration.

Risks: type range assertions assume all manipulated types fall within `PAC_TYPE_BEGIN..PAC_TYPE_END`. Because blob pointers are borrowed, caller memory contexts must outlive PAC reconstruction. Duplicate PAC buffers are rejected for known supported types.

Test signals: PACs with duplicate known types, unknown types, add existing/new type, remove first/middle/last type, and order preservation when copying trusted PAC buffers.
