<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/runshell -->
# sources/sync-backup/git-annex/standalone/linux/skel/runshell

Purpose: central Linux standalone environment launcher. It prepares bundled binaries, libraries, Git templates, man pages, locales, CA certificates, Android/Termux adaptations, and SSH helper shims before executing a requested command or shell.

Important behavior: validates `base/bin/git-annex`, canonicalizes `base`, and works around `:` or `;` in paths by symlinking through a temp directory. Unless `GIT_ANNEX_PACKAGE_INSTALL` is set, it installs `~/.ssh/git-annex-shell` and `~/.ssh/git-annex-wrapper` shims. It exports `GIT_ANNEX_APP_BASE`, prepends `$base/bin`, appends `$base/extra`, builds `GIT_ANNEX_LD_LIBRARY_PATH` from `libdirs`, sets `GIT_ANNEX_DIR`, `GCONV_PATH`, `GIT_EXEC_PATH`, `GIT_TEMPLATE_DIR`, and `MANPATH`, and unsets `LD_PRELOAD`.

Control flow: after environment setup, it optionally creates a per-bundle locale cache under `~/.cache/git-annex/locales`, using `buildid`, `gconvdir`, `i18n`, and `localedef` for UTF-8 locales. On Android, it removes incompatible bundled Git pieces, removes bundled `uname`, runs `termux-fix-shebang`, may add the bundle to `.profile`, uses `proot`, sets `GIT_ANNEX_SSH_SOCKET_DIR`, and narrows `GIT_ANNEX_STANDLONE_ENV`. For non-Android it sets CA info from system locations or bundled certs. Finally it restores `IFS`, exports `LD_HWCAP_MASK=`, and execs the requested command or `sh`; when a temp symlink was used, it runs without `exec` so the EXIT trap can clean it.

State and persistence: writes SSH shims, locale caches, Android `.profile` entries, and may mutate the extracted Android bundle by deleting bundled Git-related files and fixing shebangs. It also creates temporary symlink directories for problematic paths.

Dependencies and integration points: POSIX shell, Linux dynamic linker behavior, bundled metadata files (`libdirs`, `gconvdir`, `buildid`), `localedef`, Termux utilities on Android, `proot`, Git, git-annex assistant/webapp, SSH forced-command workflows, and Git SSL certificate discovery.

Risks: this script has broad side effects in `$HOME/.ssh`, `$HOME/.cache`, and on Android inside the bundle. Locale cache creation has race handling but still depends on filesystem semantics. The variable name `GIT_ANNEX_STANDLONE_ENV` is misspelled consistently and likely part of an existing contract. Android cleanup uses `find | grep | xargs rm -rf`, which is intentionally broad inside the bundle.

Test signals: run commands through the standalone bundle on Linux and Android/Termux, verify library path and Git template behavior, locale cache generation/cleanup, CA fallback, SSH shim creation, temp path workaround for colon paths, and package-install mode with system locales.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/linux/skel/runshell -->
