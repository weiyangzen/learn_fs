# File Research: sources/os/bsd/freebsd-src/sbin/etherswitchcfg/ifmedia.c

Provides media-word parsing and formatting helpers for `etherswitchcfg`, derived from ifconfig/ifmedia code.

Key responsibilities:
- Maps top-level media types to subtype, alias, option, and mode description tables.
- Parses user media subtype strings with `get_media_subtype()`.
- Parses media mode strings with `get_media_mode()`.
- Parses comma-separated option lists with `get_media_options()`.
- Performs case-insensitive lookup with `lookup_media_word()`.
- Prints media words in compact switch-config format via `print_media_word()`.
- Prints ifconfig-style media words via `print_media_word_ifconfig()`.

Important data:
- Description arrays initialized from kernel macros such as `IFM_TYPE_DESCRIPTIONS`, `IFM_SUBTYPE_ETHERNET_DESCRIPTIONS`, and related aliases/options.
- `ifmedia_types_to_subtypes[]` supports Ethernet, IEEE80211, and ATM style mappings plus shared types/options.

Notable behavior:
- `get_media_options()` copies the input because it tokenizes with `strtok()`.
- Unknown subtypes and types terminate with `errx()`.
- Unknown mode returns `-1`, letting callers decide behavior.
- Printers suppress alias entries when rendering canonical names.

Risks and constraints:
- Contains a large `#if 0` block of copied ifconfig functionality retained as reference but not compiled.
- The type-to-subtype table must remain consistent with `IFM_TYPE_DESCRIPTIONS` order.
- This is duplicated logic rather than linking a shared media parser.
