# sources/storage-engines/foundationdb/packaging/deb/DEBIAN-foundationdb-clients/postinst

Purpose: This Debian client-package post-install script runs linker cache maintenance and initializes the shared FoundationDB system user/group and configuration directory on first install.

Important operations: On `configure`, it calls `ldconfig`. When there is no previously configured version (`$2` empty), it creates system group `foundationdb`, creates system user `foundationdb` with disabled login and `/var/lib/foundationdb` home, then sets `/etc/foundationdb` ownership and mode `775`.

Control flow: The script only acts for the `configure` maintainer-script action. Upgrade or abort actions fall through successfully.

State and persistence behavior: It persists OS-level passwd/group entries and directory ownership/permissions. It does not create a cluster file.

Dependencies and integration points: It depends on Debian tools `getent`, `addgroup`, `adduser`, `chown`, `chmod`, and `ldconfig`. The server package defensively repeats user/group creation.

Risks: Permission mode `775` allows group writes to `/etc/foundationdb`, which is intentional for the service group but security-sensitive. Tests should run package install in a container and verify idempotence for fresh install versus upgrade.
