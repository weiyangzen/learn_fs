## sources/test-tools/kdevops/workflows/kdevops/scripts/jounal-ls.sh

Purpose: Lists remote journal symlinks and their backing file sizes/IP addresses.

Important APIs/types/functions: Takes one `DIR` argument, reads `kdevops_host_prefix` from `extra_vars.yaml`, and uses `find`, `readlink`, `du`, and formatted `printf`.

Control flow: Validates one argument, computes a host prefix, finds symlinked journal files matching the prefix, skips names containing `@`, resolves each link, gets size, derives IP from the real filename, and prints a table.

State and persistence: Read-only aside from command output.

Dependencies and integration points: Depends on `extra_vars.yaml`, symlinks created by `jounal-ln.sh`, and remote journal naming.

Risks and test signals: The early `FILES=$(find ... $IP ...)` references unset `IP` and is unused; path stripping assumes exact `$DIRremote-` concatenation. Test with real symlink paths and confirm IP extraction.
