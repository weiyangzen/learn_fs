# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/ifieee80211.c

`ifieee80211.c` is the full ifconfig module for net80211 wireless devices. It registers a large `ieee80211_cmds[]` table, an `af_ieee80211` status callback, and a `wlan` clone callback for virtual AP/device creation.

The file wraps net80211 ioctl access through `lib80211_get80211()`, `lib80211_get80211len()`, `lib80211_get80211val()`, and `lib80211_set80211()`. Cached module state includes channel info, regulatory domain, roaming params, tx params, current channel, HT/VHT config, and the current ifmedia state.

Channel handling is substantial. `getchaninfo()`, `mapfreq()`, `mapchan()`, `promote()`, `getchannelflags()`, and `getchannel()` parse channel/frequency specifications with mode and width suffixes, promote ambiguous legacy channels to better HT/VHT-capable entries, and validate against the kernel channel list.

Regulatory-domain handling uses `lib80211_regdomain` data. `set80211regdomain()`, `set80211country()`, `set80211location()`, and `set80211ecm()` modify cached `regdomain`, then `setregdomain_cb()` fetches device capabilities, builds a legal channel list with `regdomain_makechannels()`, and pushes `IEEE80211_IOC_REGDOMAIN`.

Configuration commands cover SSID/mesh ID, station name, auth mode, powersave, WEP keys and NetBSD-compatible `nwkey`, BSSID, channel switching, tx power, roaming mode, WME/WMM parameters, ACL MAC policy/list edits, background scan, quiet timing, tx/roam rates, RTS/fragment/BMISS thresholds, HT/VHT toggles, AMPDU/AMSDU/STBC/LDPC/UAPSD, TDMA, mesh routing, HWMP, and clone parameters.

Status and list output are broad. `ieee80211_status()` prints SSID/mesh ID, channel, BSSID, station name, regulatory domain, auth/privacy/key status, powersave, tx power, tx params, scan/roam settings, HT/VHT feature state, WME, AP/TDMA/mesh settings, and parent device. `set80211list()` dispatches to station, scan/AP cache, channel/frequency, active channel, caps, WME, MAC ACL, tx power, roam, tx params, regdomain, country list, and mesh route listings.

The file contains extensive IE decoders for scan/station output: WPA, RSN, RSNXE, WPS, WME, Atheros, TDMA, HT/VHT, HE capability/operation, MU-EDCA, supported operating classes, country, BSS load, AP channel report, and generic element dumps in verbose mode.

Virtual AP clone support accumulates `struct ieee80211_clone_params`. `wlan_create()` requires `wlandev`, requires `wlanbssid` for WDS, calls `ifcreate_ioctl()`, then sets a default FCC/US regulatory domain if the driver left defaults unset.

Notable implementation details: string/key parsing accepts printable strings or `0x` hex; `print_string()` honors UTF-8 locales; line wrapping is handled by `LINE_INIT`, `LINE_CHECK`, and `LINE_BREAK`; several setters register callbacks so combined command-line options update one fetched structure once.

Risk notes: this is a dense legacy C command surface with many direct `atoi()`/`atof()` conversions, fixed local buffers, and protocol structure casts. Mesh metric/path setters copy exactly 12 bytes from the input pointer, so callers rely on kernel/userland command syntax discipline. The scan and IE decoders trust kernel-filtered IE lengths in several paths, which matches the comments but is an important assumption.
