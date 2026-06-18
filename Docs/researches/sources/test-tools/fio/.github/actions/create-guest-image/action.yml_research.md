# `sources/test-tools/fio/.github/actions/create-guest-image/action.yml`

Purpose: Composite GitHub Action that creates a libguestfs VM image for fio guest testing.

Important APIs and inputs: Inputs are `distro` defaulting to `debian-12` and optional `extra_pkgs`. Steps install `libguestfs-tools`, relax permissions on `/boot/vmlinuz*` and `/dev/kvm`, generate an SSH key, and run `virt-builder` with hostname, SSH injection, host key generation, Debian network interface adjustment, and environment variables for GitHub and CI context.

Control flow: The QEMU workflow calls this before building QEMU and starting the VM. The generated image is named according to the distro by `virt-builder` defaults and then passed to the start-VM action.

State and persistence: Produces a guest image file in the runner workspace and writes an SSH key under `~/.ssh`. Environment entries persist inside the guest image.

Dependencies and integration: Depends on Ubuntu runner privileges, libguestfs image templates, KVM, SSH tooling, and caller-provided CI environment variables.

Risks and test signals: `chmod 0666 /dev/kvm` and broad `/boot/vmlinuz*` readability are CI-specific privilege changes. The network-interface sed assumes a Debian interface name. Tests should boot the produced image, verify SSH access, check injected environment variables, and confirm extra packages are installed by later guest scripts.
