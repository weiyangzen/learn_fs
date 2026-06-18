# sources/test-tools/kdevops/scripts/status_nixos.sh

## Purpose
Displays libvirt status for NixOS-backed kdevops virtual machines, networks, and storage pools.

## Important APIs and control flow
The script computes `SCRIPTS_DIR=$(dirname $0)`, sources `libvirt_pool.sh`, runs `get_pool_vars`, detects the libvirt URI through `detect_libvirt_session.sh` when present, exports `LIBVIRT_DEFAULT_URI`, then prints filtered `virsh list --all`, `virsh net-list --all`, and `virsh pool-list --all` output.

## State and dependencies
It is read-only over libvirt state and depends on `virsh`, optional sudo capability, and helper variables from `libvirt_pool.sh`. It does not persist state itself.

## Integration points
This wrapper gives Make targets or users a stable `scripts/status_nixos.sh` entry point for NixOS VM, network, and pool status.

## Risks and test signals
Unquoted `$0` and helper paths can misbehave if the checkout path contains whitespace. The grep filters only `nixos` or `kdevops`, so custom names may be hidden. Test with user-session and system libvirt URIs and with missing `virsh`.
