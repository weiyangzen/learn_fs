# sources/storage-engines/foundationdb/packaging/deb/DEBIAN-foundationdb-server/postinst

Purpose: This Debian server-package post-install script initializes service directories, creates a default cluster file for fresh installs, starts FoundationDB, registers init defaults, and configures a new single-memory database when needed.

Important operations: It creates the `foundationdb` user/group if needed, owns `/var/lib/foundationdb` and `/var/log/foundationdb`, locks down data/log directories to `0700`, generates `/etc/foundationdb/fdb.cluster` if absent, starts via `deb-systemd-invoke`/`systemctl` or init.d, calls `update-rc.d`, and runs `fdbcli configure new single memory; status` for a new database.

Control flow: All behavior is under `configure`. First-install-only blocks are gated by empty `$2`; service start runs on configure for both fresh install and upgrade.

State and persistence behavior: It persists OS user/group, data/log ownership, cluster file contents, init registration, service state, and potentially a newly configured FDB database. Existing cluster files are preserved.

Dependencies and integration points: It integrates Debian maintainer scripts with systemd/init.d, `fdbcli`, `/etc/foundationdb/fdb.cluster`, and package-created directories.

Risks: Automatically configuring `single memory` is suitable for local first install but not a production cluster. Random cluster token generation uses filtered `/dev/urandom`. Tests should verify fresh install, upgrade with existing cluster file, systemd and non-systemd paths, and failure behavior when `fdbcli` cannot configure within timeout.
