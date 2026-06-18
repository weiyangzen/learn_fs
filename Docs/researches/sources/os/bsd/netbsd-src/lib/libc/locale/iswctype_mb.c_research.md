# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/iswctype_mb.c

Read completely: 235 lines.

This file implements locale-aware wide classification, translation, and width APIs. Macros generate `iswalnum_l` through `iswxdigit_l`, plus non-`_l` wrappers. Similar macros generate `towupper_l`/`towlower_l`. It also implements `wctype`, `wctrans`, `iswctype`, `towctrans`, `wcwidth`, and `wcswidth`.

Important interactions: uses `_RuneLocale` from `loc->part_impl[LC_CTYPE]`, `_iswctype_priv` for classification, `_towctrans_priv` for translations, and `_runetype_priv` for width data.

Security/reliability notes: null `wctype_t`/`wctrans_t` set `EINVAL`. `wctrans_l` appears to return `&rl->rl_wctype[i]` rather than `&rl->rl_wctrans[i]`, which is a notable type/logic risk for charmaps. Width accumulation uses `int` and does not check overflow.
