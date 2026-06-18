# sources/test-tools/xfstests-bld/fstests-bld/update-all

Purpose: top-level build/update script for the fstests appliance userland components. It builds and installs dependency projects into a local `bld` destination, then records git version metadata for key repositories.

Important steps: source `config.custom` or `config`, compute parallelism from CPU count, set `DESTDIR`, build/install `e2fsprogs-libs`, `attr`, `acl`, `libaio`, `xfsprogs-dev`, `fio`, `xfstests-dev`, `quota`, and `misc`, remove `.la` files, and write `xfsprogs.ver`, `fio.ver`, `xfstests.ver`, and `quota.ver`.

Control flow/state: the script is run with `bash -vx`, so commands are echoed. Each component build runs in a subshell. Installed artifacts persist under `$(pwd)/bld`; version files persist in the fstests-bld directory.

Dependencies/integration: depends on repository checkout layout, make/libtool, config variables such as `EXEC_LLDFLAGS`, and git metadata. Outputs feed test appliance/release artifacts.

Risks: no `set -e`, so failures may not stop subsequent component builds. Hard-coded static linking/libtool flags can be host-sensitive. Parallel builds can expose race issues. Removing all `.la` files is broad but intentional.

Test signals: successful end-to-end appliance builds and version-file freshness in release scripts are the primary validation.
