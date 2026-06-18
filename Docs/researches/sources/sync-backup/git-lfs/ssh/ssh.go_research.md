# sources/sync-backup/git-lfs/ssh/ssh.go

Purpose: constructs SSH executable names and arguments for Git LFS authentication/transfer commands across OpenSSH, plink, tortoiseplink, and custom shell commands.

Important APIs/types/functions: `sshVariant`, `SSHMetadata`, `FormatArgs`, `GetLFSExeAndArgs`, `parseShellCommand`, `findVariant`, `autodetectVariant`, `getVariant`, `findRuntimeDir`, `getControlDir`, `GetExeAndArgs`, `defaultSSHCmd`, and `sshOptPrefixRE`.

Control flow: command selection honors `GIT_SSH_COMMAND` before `GIT_SSH`, then `core.sshcommand`, then `ssh`. Variant is selected by `GIT_SSH_VARIANT`, `ssh.variant`, or basename autodetection. Args add tortoise `-batch`, optional OpenSSH multiplexing options/control path, variant-specific port flags, host separator/stripping for option-looking hostnames, then the remote command.

State/persistence behavior: may create a temporary control socket directory under `XDG_RUNTIME_DIR`, `/tmp` on Darwin, or default temp. It otherwise only returns command data.

Dependencies/integration: used by `connection.go`, URL parsing in `lfshttp`, shell quoting in `subprocess`, and tests covering option injection.

Risks: `GIT_SSH_COMMAND` and `core.sshcommand` require shell wrapping, so quoting correctness is security-sensitive. Hostnames beginning with dashes are guarded with `--` for OpenSSH and stripped for other variants to prevent option injection.

Test signals: `ssh_test.go` has broad table-style coverage for variants, ports, multiplexing, precedence, shell commands, custom SSH, and malicious option-like host/path input.
