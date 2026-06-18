# sources/user-network-fs/samba/source3/winbindd/nss_info_template.c

## Purpose
This is the built-in fallback NSS-info backend. It registers the `template` backend and returns `NT_STATUS_NOT_IMPLEMENTED` for alias mapping operations.

## Important APIs, Types, And Functions
`nss_template_init` and `nss_template_close` return OK. `nss_template_map_to_alias` and `nss_template_map_from_alias` return not implemented. `nss_info_template_init` registers `nss_template_methods`.

## Control Flow
The backend performs no transformation. Registration is invoked when the NSS-info registry needs the template backend and it has not yet been registered.

## State And Persistence
No state or persistence is used.

## Dependencies And Integration
It depends on `nss_info.h` and `smb_register_idmap_nss`. It provides a safe static module for the NSS-info registry's default/fallback path.

## Risks And Test Signals
Test successful registration, duplicate registration behavior through the registry, and callers that handle `NT_STATUS_NOT_IMPLEMENTED` from alias mapping. This backend is intentionally inert.
