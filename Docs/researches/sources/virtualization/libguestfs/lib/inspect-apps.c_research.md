# File Research: sources/virtualization/libguestfs/lib/inspect-apps.c

Purpose: Implements guest application/package inventory for Linux/Hurd package managers and Windows registry uninstall keys.

Key behavior:
- Deprecated `inspect_list_applications` wraps `inspect_list_applications2` and translates the newer struct to the older ABI.
- Dispatches by inspected OS type and package format: RPM via daemon internal action, Debian dpkg status parsing, pacman local database parsing, Alpine APK installed database parsing, and Windows registry parsing.
- dpkg and APK files are downloaded with 50 MB safety limits; pacman desc files are downloaded with an 8 KiB limit.
- Debian parsing handles installed status, version epoch/release splitting, architecture, homepage, source package, summary, and multiline descriptions.
- Pacman parsing reads `%KEY%` blocks and splits `[epoch:]ver-rel`.
- APK parsing reads one-letter fields and strips leading `r` from release revisions.
- Windows parsing opens the SOFTWARE hive with hivex, reads native and WOW64 uninstall paths, collects display/version/location/publisher/URL/comments, and adds a Windows Defender heuristic.
- Antivirus classification uses compiled PCRE2 regexes across name, display name, and publisher.
- Results are normalized through `add_application` and sorted by application name.

Dependencies and state:
- Depends on inspection getters, generated filesystem/download/hivex actions, `guestfs_int_download_to_tmp`, version parsing, PCRE2 match helpers, and struct cleanup helpers.
- No persistent handle state except hivex open/close side effects in the appliance.

Risks:
- Package database parsers are permissive and skip malformed entries.
- Windows inventory is heuristic and limited to uninstall registry keys plus Defender.
- Some fields are explicitly unimplemented or reserved, such as translated path and some source/summary coverage.
