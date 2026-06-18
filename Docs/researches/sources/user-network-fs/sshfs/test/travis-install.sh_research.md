# sources/user-network-fs/sshfs/test/travis-install.sh

## Purpose

`travis-install.sh` is a legacy CI provisioning script for SSHFS. It builds and installs libfuse from the upstream master branch, adjusts pkg-config and dynamic-loader paths for the installed library, and configures localhost SSH key-based authentication so the integration tests can mount `localhost:<tmpdir>` without a password prompt.

## Important APIs, Types, And Functions

- `set -e` fails the provisioning run on any unhandled command error.
- `wget https://github.com/libfuse/libfuse/archive/master.zip` downloads libfuse source as a zip archive.
- `meson ..`, `ninja`, and `sudo ninja install` configure, build, and install libfuse.
- `sudo mv /usr/local/lib/*/pkgconfig/* /usr/local/lib/pkgconfig/` normalizes pkg-config file placement for later Meson discovery.
- `printf '%s\n' /usr/local/lib/*-linux-gnu | sudo tee /etc/ld.so.conf.d/usrlocal.conf` and `sudo ldconfig` add the installed library directory to the runtime linker cache.
- `ssh-keygen`, appending to `~/.ssh/authorized_keys`, chmod, and an SSH smoke test prepare passwordless localhost access.

## Control Flow

The script downloads `master.zip`, unzips it, enters `libfuse-master`, creates and enters `build`, configures with Meson, builds with Ninja, and installs with sudo. After installation it ensures `/usr/local/lib/pkgconfig` exists, moves architecture-specific pkg-config files into that directory, writes the `/usr/local/lib/*-linux-gnu` path to a loader config file, and runs `ldconfig`.

The second phase generates a 1024-bit RSA key at `~/.ssh/id_rsa` with an empty passphrase, appends the public key to `~/.ssh/authorized_keys`, tightens authorized-key permissions to `600`, and runs `ssh -o "StrictHostKeyChecking=no" localhost echo "SSH connection succeeded"` as an end-to-end authentication check.

## State And Persistence Behavior

This script makes durable changes to the CI host. It creates `master.zip`, a `libfuse-master` source tree, and a `libfuse-master/build` directory in the current working directory. It installs libfuse under `/usr/local`, moves pkg-config metadata, writes `/etc/ld.so.conf.d/usrlocal.conf`, and updates the loader cache. It also creates or overwrites `~/.ssh/id_rsa`, appends to `~/.ssh/authorized_keys`, and may add a `localhost` host key to the user's known-hosts file.

The script is not idempotent in a clean sense: rerunning can fail if `~/.ssh/id_rsa` already exists and `ssh-keygen` prompts, can append duplicate authorized keys, and can fail if `master.zip` or `libfuse-master` already exist in conflicting states.

## Dependencies And Integration Points

- Requires POSIX shell, wget, unzip, Meson, Ninja, sudo, a compiler toolchain for libfuse, OpenSSH client/server, and permission to write `/usr/local` and `/etc/ld.so.conf.d`.
- Provides libfuse headers/libraries needed by the SSHFS Meson build.
- Provides the passwordless localhost SSH precondition required by `test_sshfs.py`.
- The script pairs with `travis-build.sh` in release packaging and legacy CI setup.

## Risks And Edge Cases

- Building from libfuse `master` is non-reproducible; upstream changes can break SSHFS CI without a local repository change.
- The 1024-bit RSA key is weak by modern standards and is appropriate only for disposable CI, not developer machines.
- Overwriting or appending to real user SSH configuration is risky outside isolated CI.
- The pkg-config move assumes a specific `/usr/local/lib/*/pkgconfig` layout and may fail or move multiple architecture directories unexpectedly.
- `StrictHostKeyChecking=no` eases CI setup but suppresses host-key verification.
- No cleanup is performed, so repeated runs can accumulate source/build artifacts and SSH authorized-key duplicates.

## Test Signals

- Successful Meson/Ninja libfuse build and `sudo ninja install` indicate the FUSE dependency is available for the SSHFS build.
- `ldconfig` completing after writing the loader path indicates runtime linking should find the installed libfuse.
- The final `ssh localhost echo "SSH connection succeeded"` verifies the exact authentication path later used by `test_sshfs.py`.
