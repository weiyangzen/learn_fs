# sources/test-tools/kdevops/scripts/update_ssh_config_guestfs.py

## Purpose
Generates SSH config entries for libvirt/guestfs kdevops guests by querying guest IP addresses through the QEMU guest agent.

## Important APIs
`get_addr(name)` repeatedly runs `virsh qemu-agent-command <name> guest-network-get-interfaces` until it finds the first non-loopback IPv4 address or exceeds `KDEVOPS_SSH_CONFIG_TIMEOUT` seconds. `main()` reads `extra_vars.yaml`, loads the nodes file, and writes stanzas from `ssh_template`.

## Control flow
The script resolves `TOPDIR`, reads `extra_vars.yaml`, opens the configured `kdevops_nodes` YAML, chooses `~/.ssh/config_kdevops_<topdir_path_sha256sum>`, then iterates `nodes["guestfs_nodes"]`. Each host stanza includes host alias, IP alias, username `kdevops`, SSH port, guestfs identity file, disabled known-host checking, and fatal log level.

## State and persistence
It overwrites the generated SSH config and chmods it `0600`. It polls live VM agent state and may wait up to 180 seconds by default.

## Dependencies and integration
Requires PyYAML, `/usr/bin/virsh`, QEMU guest agent support, `extra_vars.yaml`, and the generated guestfs nodes file.

## Risks and test signals
JSON parsing assumes successful virsh output is valid and shaped with `return`. It picks the last matching IPv4 encountered. Test with guests that boot slowly, guests without agent networking, custom SSH port, and generated config permission checks.
