# sources/sync-backup/git-lfs/ssh/ssh_test.go

Purpose: verifies SSH command construction and SSH URL metadata handling.

Important tests: `TestSSHGetLFSExeAndArgs`, many `TestSSHGetExeAndArgs*` cases for OpenSSH/plink/tortoiseplink/simple variants, multiplexing master/extra/no-multiplexing cases, command precedence tests, custom SSH tests, invalid option-like host/path tests, and bare SSH URL parsing.

Control flow: tests construct `lfshttp.Client` instances with controlled OS/Git environment maps, fill `ssh.SSHMetadata`, call `GetExeAndArgs` or `GetLFSExeAndArgs`, normalize with `FormatArgs` when needed, and assert exact executable/argument arrays.

State/persistence behavior: no filesystem persistence except temporary control paths generated in multiplexing cases. Tests assert non-empty control path or exact provided path.

Dependencies/integration: covers `lfshttp.EndpointFromSshUrl`, `EndpointFromBareSshUrl`, `ssh.FormatArgs`, and environment/config precedence.

Risks: exact argument assertions are intentionally brittle; legitimate command-line behavior changes need test updates. Multiplexing tests avoid platform-specific socket validation and focus on generated args.

Test signals: protects against regressions in command precedence, port flag selection, OpenSSH control options, shell wrapping, and option-injection vulnerabilities.
