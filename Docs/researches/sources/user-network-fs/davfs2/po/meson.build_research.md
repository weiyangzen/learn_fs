<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/po/meson.build -->
# Research: sources/user-network-fs/davfs2/po/meson.build

Purpose: Meson NLS build fragment for generating gettext catalogs for davfs2.

Important APIs: `i18n = import('i18n')` and `i18n.gettext(meson.project_name(), preset: 'glib')`. It sets `po_dir = meson.current_source_dir()`, though that variable is not used in this fragment.

Control flow and integration: entered from root `meson.build` only when `enable_nls` is true, which requires option `nls=true` and a found `msgfmt`. The domain name is the Meson project name, `davfs2`.

State and persistence: produces build/install translation artifacts, usually `.gmo`/`.mo`, derived from PO files and `POTFILES.in`.

Dependencies: Meson i18n module, gettext/msgfmt, valid PO files, and a complete `POTFILES.in`.

Risks: `preset: 'glib'` assumes GLib gettext conventions; this should be intentional because the C code uses plain gettext macros. If no LINGUAS/PO files are present or stale, installed catalogs may be incomplete.

Test signals: NLS-enabled Meson build, gettext target execution, installed locale file inspection, and runtime smoke test with `LANG=...` to confirm translated diagnostics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/po/meson.build -->
