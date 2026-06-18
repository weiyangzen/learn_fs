# sources/user-network-fs/samba/source3/winbindd/winbindd_ads.h

Purpose: declares the ADS backend method table and the idmap ADS cached connection helper.

Important APIs and types: include guard `__WINBINDD_ADS_H__`, `#include "ads.h"`, external `struct winbindd_methods ads_methods`, and `ADS_STATUS ads_idmap_cached_connection(const char *dom_name, TALLOC_CTX *mem_ctx, ADS_STRUCT **adsp)`.

Control flow role: no implementation flow; it exposes ADS backend integration points to other winbindd/idmap code.

State and persistence: no direct state. The declared helper returns or creates cached `ADS_STRUCT` objects whose lifetime is controlled by the caller's talloc context and implementation in `winbindd_ads.c`.

Dependencies and integration points: depends on ADS types and `winbindd_methods` from `winbindd.h` users. Integrated by backend selection code and idmap AD paths that need a cached LDAP connection by domain name.

Risks: declarations are only valid when ADS support is built consistently with implementation guards. Signature changes ripple into idmap and backend registration code.

Test signals: build with and without ADS support, link-time availability of `ads_methods`, and callers correctly managing returned `ADS_STRUCT` lifetime.
