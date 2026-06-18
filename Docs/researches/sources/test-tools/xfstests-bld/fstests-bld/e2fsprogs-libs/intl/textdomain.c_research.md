# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/textdomain.c

Purpose: implements `textdomain(3)`, selecting the default message catalog domain.

Important APIs and control flow: `TEXTDOMAIN(domainname)` is name-mapped for glibc or standalone libintl. A `NULL` argument returns the current domain. Empty string or the built-in default resets `_nl_current_default_domain` to `_nl_default_default_domain`. A new non-default domain is duplicated with `strdup`/`malloc`, installed under `_nl_state_lock`, `_nl_msg_cat_cntr` is incremented on success, and the previous non-default domain is freed.

State and persistence: mutates global `_nl_current_default_domain` and `_nl_msg_cat_cntr`; locking is real in glibc and dummy in standalone builds.

Dependencies and integration: depends on `gettextP.h`, libintl headers, string allocation, and the catalog invalidation counter consumed by lookup/cache code.

Risks and test signals: standalone builds lack real thread synchronization; allocation failure leaves the old domain intact but returns `NULL`. Test reset, same-domain no-op, repeated changes, allocation failure behavior, and catalog reload notification.
