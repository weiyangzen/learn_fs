<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/setup/blobfuse2.service -->
# sources/user-network-fs/blobfuse2/setup/blobfuse2.service

## Purpose
Example systemd unit for running a Blobfuse2 mount as a service.

## Important APIs, Types, and Functions
`[Unit]` requires network-online. `[Service]` sets `WorkingDirectory`, `User`, mount/cache/config environment variables, Azure auth environment variables, log level, FUSE timeouts, `Type=simple`, `ExecStart` invoking `blobfuse2 mount`, and `ExecStop` using `fusermount -u`. `[Install]` targets `multi-user.target`.

## Control Flow and State
systemd starts Blobfuse2 with configured environment and stops by unmounting the mount point. State persists in the mounted FUSE process, cache directory, and syslog/log files.

## Dependencies and Integration Points
Requires systemd, network, Blobfuse2 installed at `/usr/local/bin/blobfuse2`, `fusermount`, a valid user, config file, mount point, cache path, and Azure credentials. Integrates with setup docs and syslog filters.

## Risks and Edge Cases
The sample includes account-key placeholders and commented SAS/MSI alternatives; users must edit carefully. SAS tokens need `%` escaping in systemd. `User=AzureUser` and paths are environment-specific. `ExecStop` uses `fusermount`, which may differ for fuse3 systems.

## Test Signals
`systemctl start blobfuse2.service`, mount visibility, and `systemctl status`/logs validate the unit.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/setup/blobfuse2.service -->
