<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/po/POTFILES.in -->
# Research: sources/user-network-fs/davfs2/po/POTFILES.in

Purpose: gettext source manifest listing C files that contain translatable strings for davfs2 Native Language Support.

Important entries: `src/cache.c`, `src/dav_fuse.c`, `src/kernel_interface.c`, `src/mount_davfs.c`, `src/umount_davfs.c`, and `src/webdav.c`.

Control flow and integration: consumed by gettext tooling via Meson `i18n.gettext()` in `po/meson.build`. It ensures `_()` strings in runtime sources are extracted into the `davfs2` text domain.

State and persistence: not runtime state; it persists the extraction scope for translators.

Dependencies: paths must match source files included in `src/meson.build`. Files using `_()` but absent here would ship untranslated messages.

Risks: build or translation drift if new translatable C files are added without updating this manifest. Because cache and WebDAV errors are operator-facing, missing translations reduce diagnostic quality.

Test signals: `meson compile davfs2-pot`/gettext extraction, compare `_(` occurrences against manifest coverage, and verify installed `.mo` files when NLS is enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/po/POTFILES.in -->
