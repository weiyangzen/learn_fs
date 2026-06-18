# sources/storage-engines/foundationdb/packaging/deb/DEBIAN-foundationdb-server/preinst

Purpose: This Debian server-package pre-install script stops the running service during upgrades, removes an obsolete bundled argparse file, and blocks installation over an old monolithic `foundationdb` package unless that package is purged.

Important operations: On `upgrade`, it runs `invoke-rc.d foundationdb stop || :` and removes `/usr/lib/foundationdb/argparse.py`/`.pyc`. It then checks `dpkg-query -s foundationdb`; if present, it prints a warning and exits with status 1.

Control flow: Upgrade-specific cleanup happens first; the old-package conflict check happens for all invocations.

State and persistence behavior: It can stop service processes and delete obsolete Python files. It does not alter database files directly, but it refuses installation when old package state could conflict.

Dependencies and integration points: It uses Debian `invoke-rc.d`, `dpkg-query`, and package filesystem paths. It coordinates package migration from older packaging layouts.

Risks: The message says purging the old package will erase databases, so this guard intentionally forces an operator decision. Tests should simulate upgrade and fresh install with/without the old package registered.
