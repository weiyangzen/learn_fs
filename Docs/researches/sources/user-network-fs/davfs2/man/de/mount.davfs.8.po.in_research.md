# sources/user-network-fs/davfs2/man/de/mount.davfs.8.po.in

## Purpose
This PO input provides the German translation for the `mount.davfs(8)` manpage, covering WebDAV mounting behavior, options, security policy, caching, locks, files, environment variables, examples, bugs, and references.

## Important APIs and structure
It is gettext/po4a data with roff references and Meson placeholders. It documents translated command forms, mount options such as `conf`, `dir_mode`, `file_mode`, `uid`, `gid`, `user`, `users`, `_netdev`, `username`, environment variables such as `DAVFS_PASSWORD`, proxy variables and `no_proxy`, plus file paths for config, secrets, certs, runtime PID files, and caches.

## Control flow described
The translated page describes how `mount` invokes the helper, how options are interpreted, how privileges drop to davfs2 user/group, how ordinary-user mounting is constrained by group membership and fstab, how cache state is reused, and how lock/lost-update recovery works.

## State and persistence behavior
It documents persistent cache directories, secrets files, certificate stores, PID files, fstab entries, and local-only permission metadata. It also documents that unmounting stores cached attributes and that local backup files can appear under `lost+found`.

## Dependencies and integration points
It is built and installed through the German manpage Meson path and must track the English `mount.davfs.8` source. Its environment variable and 2FA text must remain synchronized with the implementation, especially for scripted mounts.

## Risks
The inspected file contains untranslated `msgstr ""` entries for `DAVFS_PASSWORD` and its explanatory paragraph, and a fuzzy translation for the 2FA example that still uses the older credential example text. That means German documentation can omit or misstate newer authentication behavior. Since these entries affect password handling and CI mounting, they are higher-risk translation gaps.

## Test signals
Run po4a/msgfmt validation with fuzzy/untranslated checks, build the German manpage, and inspect rendered ENVIRONMENT and EXAMPLES sections. Add a release check that rejects fuzzy entries for security/authentication-related messages.
