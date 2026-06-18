# File Research: sources/virtualization/nvme-cli/libnvme/test/config/psk-json.c

## Purpose
Tests TLS key import/export through JSON config.

## Behavior
Reads config, iterates all hosts/subsystems/controllers, imports each controller TLS key with `libnvme_import_tls_key_versioned()`, exports it back with `libnvme_export_tls_key_versioned()`, resets the controller TLS key, then dumps config to stdout.

## Relevance
Validates that encoded TLS PSK material round-trips through libnvme’s JSON representation.
