<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/man/meson.build -->
# Research: sources/user-network-fs/davfs2/man/meson.build

Purpose: top-level manpage generation for davfs2. It builds configured English `davfs2.conf(5)`, `mount.davfs(8)`, and `umount.davfs(8)` pages and orchestrates po4a translations.

Important APIs: creates `mandata = configuration_data()` and fills it from project config and Meson options: package names, daemon user/group, system config/run/cache directories, config/secrets filenames, cert directory names, and bug-report URL. Calls `configure_file()` for three manpage templates and `run_command('po4a', 'po4a.conf', check:true)`. If NLS is enabled, enters `de` and `es` subdirectories.

Control flow and integration: invoked from root `meson.build` only when `get_option('man') == true`. It relies on root Meson variables such as `cdata`, `davfs2_sysconfdir`, `davfs2_localstatedir`, `mandir`, and `enable_nls`.

State and persistence: output manpages are build artifacts installed into `man5` and `man8`. Translation generation mutates/generated translated manpage sources in the build flow according to po4a.

Dependencies: Meson, po4a, gettext/NLS gating, and parent configuration values. It must stay aligned with options documented in `mount_davfs.c` and defaults in `defaults.h`.

Risks: `run_command('po4a', ...)` is unconditional inside the man build, so `-Dman=true` requires po4a even without NLS installation. Documentation substitution errors can misrepresent default paths and security policy. Translation subdirs only run under NLS, so non-NLS builds produce English-only manuals.

Test signals: Meson configure/build with `-Dman=true`, verify po4a availability failure behavior, install-tree layout, and rendered manpage placeholders.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/man/meson.build -->
