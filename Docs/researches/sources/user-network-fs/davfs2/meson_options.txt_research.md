<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/meson_options.txt -->
# Research: sources/user-network-fs/davfs2/meson_options.txt

Purpose: declares project-specific Meson options controlling documentation, installation paths, runtime users/groups, cache/state/cert directories, and NLS.

Important options: `man`, `doc`, `docdir`, `cachedir`, `statedir`, `certdir`, `dav_user`, `dav_group`, and `nls`. Defaults install man/docs, use `/var/cache/davfs2` and `/var/run`, relative cert directory `certs`, daemon user/group `davfs2`, and enable NLS if tooling is available.

Control flow and integration: consumed by root `meson.build`, `man/meson.build`, `etc` generation, and C `config.h` substitution. `dav_user`/`dav_group` affect privilege drop docs and runtime defaults; `cachedir`/`statedir` affect persistent cache and PID-file locations.

State and persistence: option values are persisted in Meson build configuration and compiled into generated files.

Dependencies: Meson option parser. Downstream packagers may override options to match distro policy.

Risks: changing path options changes binary/documentation behavior and can break existing systemd/tmpfiles, permissions, or package scripts. `certdir` is documented as relative to sysconfdir; absolute values may produce confusing paths. `statedir` default `/var/run` may differ from modern `/run` policy.

Test signals: option override matrix, install-tree inspection, and runtime smoke tests verifying cache, state, cert, and config paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/meson_options.txt -->
