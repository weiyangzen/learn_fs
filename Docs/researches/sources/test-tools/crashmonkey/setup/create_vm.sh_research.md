# sources/test-tools/crashmonkey/setup/create_vm.sh

Purpose: sudo shell script to build an Ubuntu KVM VM image with vmbuilder and project-specific network/user/package settings. It moves the generated qcow2 to a named workspace image on success.

Important APIs/types/functions: arguments `NAME` and `IP`, variables `CUR_DIR`, `DIR`, `WORKSPACE`, `sudo vmbuilder kvm ubuntu`, package options, bridge/network settings, `--copy rcs`, `mv`, and `chown`.

Control flow: computes paths, invokes vmbuilder with fixed architecture, memory, root size, Ubuntu Trusty suite, packages, bridge `br0`, IP/gateway/DNS, hostname, and copied files. If vmbuilder exits 0, it renames the qcow2 and chowns the workspace back to the invoking user.

State/persistence behavior: creates VM disk images and modifies filesystem ownership under the workspace. Dependencies/integration: requires sudo, vmbuilder/libvirt/KVM, bridge network, placeholder `<USER_NAME>` replacement, and an `rcs` file/directory.

Risks/test signals: no argument validation, hard-coded network/device/user placeholders, and destructive `--overwrite`. Failures are visible through vmbuilder exit and shell trace from `set -x`.
