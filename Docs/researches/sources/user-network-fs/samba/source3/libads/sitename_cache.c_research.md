# sources/user-network-fs/samba/source3/libads/sitename_cache.c

## Purpose

`sitename_cache.c` stores and retrieves the AD client site name associated with a realm/domain so future DC discovery can start with site-aware DNS SRV lookups.

## Important APIs, Types, and Functions

`sitename_store` writes or deletes a site name. `sitename_fetch` reads a cached site name, defaulting an empty realm to `lp_realm()`. `stored_sitename_changed` compares a candidate site name with the cached value. Internal `sitename_key` builds uppercase gencache keys using `AD_SITENAME/DOMAIN/%s`.

## Control Flow

Store rejects empty realms, deletes the cache key for empty site names, and otherwise writes the value with `get_time_t_max()` expiration. Fetch normalizes the query realm, reads gencache into the caller's talloc context, and logs hit or miss. Change detection fetches the current value and compares NULL/non-NULL and string mismatch cases.

## State and Persistence Behavior

State persists in Samba's generic cache (`gencache`) with effectively indefinite expiration. CLDAP discovery in `ldap.c` rewrites the cached site whenever a new reply reports client site data.

## Dependencies and Integration Points

It depends on `lib/gencache.h`, loadparm realm settings, talloc, and Samba string helpers. It integrates with ADS DC discovery and site-fallback logic in `ads_find_dc`.

## Risks and Test Signals

Risks include indefinite stale site names after AD subnet changes, realm/workgroup aliases producing separate cache keys, deletion on empty CLDAP site replies, and uppercase normalization expectations. Tests should cover store/fetch/delete, empty realm fallback, case-insensitive realm key behavior, changed detection for NULL and string cases, and discovery fallback when a cached site has no live DC.
