# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gen-ssh-keys

Purpose: generates missing SSH host keys according to `sshd_config`.

Important APIs/flow: `get_config_option` extracts case-insensitive `HostKey` values from `/etc/ssh/sshd_config`; `host_keys_required` returns configured paths or OpenSSH defaults; `create_key` conditionally runs `ssh-keygen` for a requested file if it is required and absent, restores SELinux context if `restorecon` exists, and prints fingerprint; `create_keys` covers RSA, DSA, ECDSA, and ED25519.

State and dependencies: writes `/etc/ssh/ssh_host_*` private/public keys. Depends on Perl, `ssh-keygen`, optional `restorecon`, and OpenSSH config format.

Integration points: enabled as `gen-ssh-keys.service` by appliance image build scripts so cloned images do not share host keys.

Risks and test signals: parser is simple and may not handle all sshd include semantics. DSA key generation may be undesirable on modern systems but only occurs if required. Tests should remove keys in a disposable root and verify configured/default key creation.
