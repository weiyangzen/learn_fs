<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/examples/localhost_helper.sh -->
# sources/test-tools/pynfs/examples/localhost_helper.sh

Purpose: server-helper script for pynfs tests against local Linux knfsd. It lets tests restart the local NFS server, manipulate files on the server side, or expire a specific NFSv4 client.

Important APIs/types/functions: `expire_client()` scans `/proc/fs/nfsd/clients/*/info` for a matching `name: "client"` line and writes `expire` to the sibling `ctl` file. The command dispatch supports `reboot`, `unlink`, `rename`, `link`, `chmod`, and `expire`.

Control flow/state: the first argument is ignored server name, the second is command, and remaining arguments are command operands. `reboot` runs `sudo systemctl restart nfs-server.service`; file operations run locally.

Dependencies/integration: assumes passwordless sudo for nfs-server restart when needed and Linux nfsd procfs client controls. It is used via pynfs `--serverhelper` options.

Risks/test signals: arguments are unquoted, so spaces or shell metacharacters in filenames are unsafe. Failure signals appear as helper command failures observed by the calling pynfs test.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/examples/localhost_helper.sh -->
