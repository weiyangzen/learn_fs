# sources/test-tools/kdevops/scripts/update_ssh_config_nixos.py

## Purpose
Manages SSH config entries for native QEMU NixOS VMs, with explicit update and remove actions.

## Important APIs
`update_ssh_config(action, hostname, host_ip, port, username, ssh_config_path, ssh_key_path, tag)` uses a `# kdevops-managed: <tag> - <hostname>` marker plus a regex to replace or remove managed blocks. `main()` validates arguments, fills defaults, and handles errors.

## Control flow
The script expands the config path, creates its parent directory, reads existing content if present, removes any matching managed entry, then either writes a new stanza for `update` or only writes the reduced content for `remove`.

## State and persistence
It rewrites the supplied SSH config file. Unlike the guestfs script, it does not chmod the file. Entries include `StrictHostKeyChecking no`, `/dev/null` known-hosts, and `LogLevel ERROR`.

## Dependencies and integration
Uses Python standard library. It is called by NixOS VM lifecycle code that knows host-forwarded SSH port and private key location.

## Risks and test signals
The argument length check uses `< 8` but usage lists eight post-program fields; missing tag is allowed by code. Regex removal assumes the marker format remains unchanged. Test update idempotency, remove, default host/user/port behavior, and config directory creation.
