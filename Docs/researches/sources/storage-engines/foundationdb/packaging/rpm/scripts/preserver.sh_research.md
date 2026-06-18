<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/rpm/scripts/preserver.sh -->
# Research: sources/storage-engines/foundationdb/packaging/rpm/scripts/preserver.sh

## Purpose
Standalone server preinstall/preun-style fragment handling user creation, legacy cleanup, config migration, and service removal on erase.

## Important APIs, Types, And Functions
Creates service account, removes old bundled `argparse.py` on upgrade, saves very old configs, and when `$1 -eq 0` stops/disables the service via systemd or SysV tools.

## Control Flow
Uses RPM `$1` to distinguish upgrade/install/erase actions and probes `pidof systemd` for service manager.

## State And Persistence Behavior
Mutates service account state, `/usr/lib/foundationdb` cleanup files, `/etc/foundationdb/foundationdb.conf.rpmsave`, and service enable/running state.

## Dependencies And Integration Points
Depends on RPM arguments, rpm query command, systemd/SysV service tools, and account tools. Overlaps with spec `%pre server` and `%preun server` logic for split script packaging.

## Risks And Edge Cases
Moving config for only versions 0.1.4/0.1.5 is narrow. `pidof systemd` is an imprecise container/systemd check. Service stop errors are suppressed.

## Test Signals
Validated by upgrade from old versions and uninstall tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/rpm/scripts/preserver.sh -->
