<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/gen_ssh_key.sh -->
# sources/test-tools/kdevops/scripts/gen_ssh_key.sh

Purpose: generates the kdevops SSH private key configured by `KDEVOPS_SSH_PRIVKEY`.

Important APIs and functions: sources `${TOPDIR}/.config` and `${TOPDIR}/scripts/lib.sh`, prints the key path, then runs `ssh-keygen -t rsa -C generated-by-kdevops -f $KDEVOPS_SSH_PRIVKEY -q -N ""`.

Control flow: linear source/configure/generate sequence.

State and persistence: writes a new RSA private/public key pair at the configured path. Existing-file behavior is delegated to `ssh-keygen`, which may prompt or fail depending on environment and options.

Dependencies and integration: bash, kdevops config, and `ssh-keygen`. It participates in provisioning identity setup.

Risks: unquoted key path fails for spaces and can be unsafe. It uses RSA without specifying bit length instead of newer ed25519 defaults used by DataCrunch helpers. No explicit parent directory creation. Test signals include running with a temp `TOPDIR` and key path, checking file permissions, existing-key behavior, and noninteractive failure modes.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/gen_ssh_key.sh -->
