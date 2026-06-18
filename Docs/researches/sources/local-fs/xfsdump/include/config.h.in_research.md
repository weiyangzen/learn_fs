# File Research: sources/local-fs/xfsdump/include/config.h.in

`config.h.in` is the generated configuration header template.

Key content:
- Defines `BITS_PER_LONG` from autoconf-provided `SIZEOF_LONG`.
- Provides `umode_t` if the platform lacks it.
- Wraps gettext support: if `ENABLE_GETTEXT` is defined, `_()` maps to `gettext`; otherwise localization macros become pass-through no-ops.
- Includes `<locale.h>`.
- Defines IRIX device major/minor conversion helpers and `IRIX_MKDEV`.
- Provides fallback `min`, `max`, and `NBBY`.

Role:
- Supplies cross-platform compatibility macros used by xfsdump source and on-media translation code.
