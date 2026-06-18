# sources/storage-engines/foundationdb/packaging/deb/DEBIAN-foundationdb-server/prerm

Purpose: This Debian pre-removal script stops FoundationDB before package removal or deconfiguration.

Important operations: For `remove` or `deconfigure`, it runs `invoke-rc.d foundationdb stop || :`.

Control flow: Other maintainer-script actions are ignored. The stop failure is tolerated to avoid blocking package operations on an already-stopped service.

State and persistence behavior: It changes only runtime service state. Database, logs, and configuration are untouched.

Dependencies and integration points: It uses Debian init policy via `invoke-rc.d` and pairs with post-install service start and post-removal init unregistering.

Risks: If stop fails silently, package removal can proceed while processes remain alive. Tests should verify remove/deconfigure actions stop services and that failed-upgrade/upgrade paths behave according to Debian policy expectations.
