<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/examples/server_helper.sh -->
# sources/test-tools/pynfs/examples/server_helper.sh

Purpose: remote-server variant of the pynfs server helper. It performs knfsd restart, file operations, and client expiration over SSH against a named server.

Important APIs/types/functions: defines and exports `expire_client()`, then dispatches `reboot`, `unlink`, `rename`, `link`, `chmod`, and `expire`. Remote operations use `ssh root@$server` for privileged restart/expire and `ssh $server` for normal file operations.

Control flow/state: first CLI argument selects the server, second selects the command, and later arguments are passed into the remote shell snippet.

Dependencies/integration: assumes SSH connectivity, appropriate root access for service restart and `/proc/fs/nfsd/clients` control, and systemd service name `nfs-server.service`.

Risks/test signals: unquoted interpolation makes filenames and client names with spaces unsafe and creates shell-injection risk in untrusted scenarios. In test labs, failures surface as server-helper nonzero exits or unchanged server-side state.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/examples/server_helper.sh -->
