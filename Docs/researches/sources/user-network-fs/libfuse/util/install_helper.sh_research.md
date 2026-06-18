# sources/user-network-fs/libfuse/util/install_helper.sh

## Purpose
Meson install helper that installs `fuse.conf`, optionally sets setuid ownership on helper binaries, creates `/dev/fuse`, installs udev rules, and installs/registers the init script.

## Important APIs, Types, And Functions
- Positional inputs: sysconfdir, bindir, udevrulesdir, useroot, initscriptdir, sbindir.
- Uses `DESTDIR`, `MESON_SOURCE_ROOT`, `install`, `chown`, `chmod u+s`, `mknod`, and `update-rc.d`.

## Control Flow
The script normalizes `DESTDIR`, installs config unconditionally, performs root-only helper setup when `useroot` is true, installs udev rules if a rules directory is known, and installs/registers the init script if requested.

## State And Persistence
Writes installation artifacts into the target filesystem, changes ownership/mode of `fusermount3` and `fuservicemount3`, may create `/dev/fuse`, and may register init startup links.

## Dependencies And Integration Points
Called from `util/meson.build` through `meson.add_install_script`. It depends on Meson environment variables and system install/admin tools.

## Risks
Setuid bit assignment is security-sensitive. Creating device nodes during staged installs may not be appropriate for all package managers. The init-script warning path prints an `init.d` path with an extra `/init.d/` component relative to the variable name, which should be checked by packagers.

## Test Signals
Run staged and non-staged installs, `useroot=true/false`, missing udev dir, missing init dir, existing and absent `/dev/fuse`, and package lint checks for setuid/device-node behavior.
