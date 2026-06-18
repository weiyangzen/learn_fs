# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/pushconfig.py

Propagates local O2CB cluster configuration to other cluster nodes over SSH.

Key constants:
- `CONFIG_FILE = '/etc/ocfs2/cluster.conf'`
- `command_template`
  - Creates `/etc/ocfs2`.
  - Writes `cluster.conf` through a shell heredoc.
  - Has an O2CB online command commented out.

Key functions:
- `get_hosts(parent=None)`
  - Gets local hostname.
  - Gets active cluster name.
  - Gets cluster nodes.
  - Returns remote node names excluding local hostname.
- `generate_command(cluster_name)`
  - Reads local cluster config.
  - Trims trailing newline.
  - Inserts content into shell heredoc command.
- `propagate(terminal, dialog, remote_command, host_iter)`
  - Starts next SSH command:
    - `ssh root@<host> <remote_command>`
  - Chains on terminal `child-exited`.
  - Marks finished when hosts exhausted.
- `push_config(parent=None)`
  - Gets hosts and generated command.
  - Shows terminal dialog.
  - Runs propagation one host at a time.
  - Warns if user tries to close before finished.

Dependencies:
- `o2cb_ctl`
- `terminal.TerminalDialog`
- VTE availability exported as `pushconfig_ok`

Notable details:
- The remote shell command embeds file contents in a heredoc; config content containing the heredoc delimiter would break the script.
- SSH target uses node names directly as `root@name`.
