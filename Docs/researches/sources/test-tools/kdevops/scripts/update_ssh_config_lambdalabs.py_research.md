# sources/test-tools/kdevops/scripts/update_ssh_config_lambdalabs.py

## Purpose
Adds, updates, or removes SSH config stanzas for Lambda Labs cloud instances.

## Important APIs
`update_ssh_config(action, hostname, ip_address, username, config_file, ssh_key, provider_name, port=22)` writes or removes entries. `remove_from_config(hostname, config_file)` deletes a block whose `Host` line starts with the hostname. `main()` parses positional arguments.

## Control flow
For `update`, the script expands paths, removes an existing block for the hostname, appends a provider-commented stanza containing hostname and IP aliases, and prints a success message. For `remove`, it removes the block and prints success.

## State and persistence
It mutates the supplied SSH config file in place. It does not create parent directories or chmod the file.

## Dependencies and integration
Uses Python standard library only. It is intended for cloud provisioning/deprovisioning steps that know instance hostname, IP, user, and private key path.

## Risks and test signals
Removal only detects `Host <hostname> ` or `Host <hostname>\t`, so entries with only `Host <hostname>` may be missed. Appending can fail if the config directory does not exist. Test update idempotency, removal, custom provider name, and custom port.
