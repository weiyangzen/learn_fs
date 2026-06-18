# sources/test-tools/kdevops/scripts/nixos_ssh_key_name.py

## Purpose
Generates a deterministic SSH key name for NixOS VMs associated with a specific kdevops checkout.

## Important APIs
`get_ssh_key_name()` computes `kdevops-nixos-<last-two-path-components>-<8-char-sha256>`. `main()` prints either the key name or, with `--path`, `~/.ssh/<key_name>`.

## Control flow and state
The script anchors naming to the script location: it takes the directory containing this script, moves one level up to the kdevops root, hashes that absolute path, and combines it with readable path suffixes. It writes no files.

## Dependencies and integration
Uses only Python standard library modules `os`, `sys`, and `hashlib`. It integrates with NixOS provisioning code that needs stable per-checkout SSH key names independent of the caller's current working directory.

## Risks and test signals
Because the path is derived from script location rather than the runtime checkout root, copied scripts or symlinks can change naming expectations. Test with and without `--path`, and ensure generated names remain stable across invocations from different directories.
