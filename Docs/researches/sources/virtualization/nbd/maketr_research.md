# File Research: sources/virtualization/nbd/maketr

Example shell script for creating an NBD transaction log.

It creates a temporary server config exporting a 50 MB file with transaction logging, flush/FUA/rotational flags, starts `nbd-server`, connects `/dev/nbd0`, formats/mounts ext3, extracts and archives a configured tarball, runs `dbench`, unmounts, disconnects the client, stops the server, removes temporary files, and lists the generated `output.tr`.

The script assumes root privileges, `/dev/nbd0`, `/mnt`, local built `nbd-server`/`nbd-client`, ext3 tools, `dbench`, and a hard-coded tarball path.
