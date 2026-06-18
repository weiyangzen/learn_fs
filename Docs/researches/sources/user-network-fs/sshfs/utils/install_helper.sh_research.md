# sources/user-network-fs/sshfs/utils/install_helper.sh

## Purpose

`install_helper.sh` is a Meson install helper for SSHFS. It creates compatibility mount helper names in the system sbin directory by symlinking `mount.sshfs` and `mount.fuse.sshfs` back to the installed `sshfs` executable. The header explicitly warns users not to call it directly because Meson supplies its arguments and installation prefix.

## Important APIs, Types, And Functions

- `set -e` stops the install script on command failure.
- `sbindir="$1"` and `bindir="$2"` consume the directories passed by Meson from `meson.add_install_script('utils/install_helper.sh', get_option('sbindir'), get_option('bindir'))`.
- `prefix="${MESON_INSTALL_DESTDIR_PREFIX}"` uses Meson's install-time destination prefix, including DESTDIR handling.
- `mkdir -p "${prefix}/${sbindir}"` ensures the target sbin directory exists.
- Two `ln -svf --relative` commands create or replace relative symlinks from `${prefix}/${sbindir}/mount.sshfs` and `${prefix}/${sbindir}/mount.fuse.sshfs` to `${prefix}/${bindir}/sshfs`.

## Control Flow

Meson invokes the script during `ninja install` after receiving the configured sbin and bin directory names. The script resolves those arguments, reads Meson's install prefix from the environment, creates the sbin directory under that prefix, then creates the two mount-helper symlinks. `-s` creates symlinks, `-v` logs the operation, `-f` replaces existing paths, and `--relative` makes the links relocatable relative to their target location.

## State And Persistence Behavior

The script mutates the install destination. It creates a directory if needed and overwrites existing `mount.sshfs` and `mount.fuse.sshfs` symlinks or files at the destination. It does not modify repository files. Its behavior depends on `MESON_INSTALL_DESTDIR_PREFIX`, so staged installs and direct installs write to different roots while preserving the same relative link relationship.

## Dependencies And Integration Points

- Requires POSIX shell plus a `ln` implementation supporting GNU `--relative`; this is not universally portable to all POSIX systems.
- Integrated by the repository's top-level `meson.build` through `meson.add_install_script`.
- Supports system mount integration conventions: tools such as `mount -t sshfs` or FUSE helper lookup can find `mount.sshfs` or `mount.fuse.sshfs` in sbin and reach the actual `sshfs` binary in bindir.
- Runs as part of `sudo ninja install` in `travis-build.sh` and normal package/install workflows.

## Risks And Edge Cases

- Argument order matters. If Meson passes bindir and sbindir in the wrong order, the script will create links in the wrong tree; the current Meson call passes sbindir first and bindir second.
- Existing non-symlink files at the mount-helper paths are force-replaced by `ln -f`.
- `MESON_INSTALL_DESTDIR_PREFIX` must be set correctly by Meson; direct manual invocation may produce empty or unintended prefixes.
- GNU `ln --relative` can limit portability on non-GNU userlands.
- The script assumes `sshfs` has already been installed at `${prefix}/${bindir}/sshfs`; if not, it still creates dangling symlinks.

## Test Signals

- `ninja install` completing verifies this script can create the sbin directory and both compatibility symlinks.
- Inspecting the install root should show `mount.sshfs` and `mount.fuse.sshfs` as relative symlinks pointing to the installed `sshfs` binary.
- Packaging or staged-install tests should confirm the links stay inside the staged `MESON_INSTALL_DESTDIR_PREFIX`.
