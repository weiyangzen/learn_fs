# sources/user-network-fs/libfuse/util/meson.build

## Purpose
Meson build definition for libfuse utility executables and install-time helper actions.

## Important APIs, Types, And Functions
- Builds `fusermount3` from `fusermount.c`, `mount_util.c`, `mount_fsmount.c`, `util.c`, and `fuser_conf.c`.
- Conditionally builds `fuservicemount3` with service mount sources and links it with `libfuse`.
- Builds `mount.fuse3` with optional service mount support.
- Computes `fuseconf_path`, udev rules directory, and install script arguments.

## Control Flow
Build logic checks `HAVE_SERVICEMOUNT` and `HAVE_NEW_MOUNT_API` in `private_cfg`, expands source lists and cflags, discovers udev rules dir if not configured, warns when unavailable, and registers `install_helper.sh`.

## State And Persistence
No runtime state. Build/install side effects include executable targets and installed config/rules/init artifacts through the install script.

## Dependencies And Integration Points
Integrates with top-level Meson options `useroot`, `udevrulesdir`, `initscriptdir`, prefix/sysconfdir/bindir/sbindir, and generated `private_cfg`.

## Risks
`mount_fsmount.c` is compiled into `fusermount3` unconditionally in the source list shown; build feature macros must ensure this is valid on systems without new mount API declarations. Service mount cflags must keep `FUSE_CONF` and `FUSERVICEMOUNT_DIR` synchronized with install paths.

## Test Signals
Configure matrix with service mount on/off, new mount API on/off, custom prefix/sysconfdir, missing udev dependency, `useroot=false`, and staged install.
