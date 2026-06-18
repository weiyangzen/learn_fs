# File Research: sources/virtualization/nbdkit/plugins/ssh/ssh.c

Implements the `ssh` nbdkit plugin, exposing a remote regular file or block device over SSH/SFTP through libssh. The plugin accepts connection parameters (`host`, `path`, `port`, `user`, `password`, `config`, `known-hosts`, `identity`, `timeout`, `compression`) plus optional remote file creation (`create`, `create-size`, `create-mode`).

Key behavior:
- `.config` parses command-line options, reads password material through `nbdkit_read_password`, collects multiple identity files, validates booleans/sizes/modes, and treats `path` as the magic config key.
- `.config_complete` requires `host` and `path`, and requires `create-size` when `create=true`.
- `.open` builds a libssh session, applies options, parses SSH config, connects, optionally verifies known hosts, authenticates with public key and/or password, creates an SFTP session, opens or creates the remote path, and records whether it is a regular file or block device.
- Host verification uses `ssh_session_is_known_server` and rejects changed, unknown, missing, or erroneous known-host states unless `verify-remote-host=false`.
- Authentication tries `none`, then public key, then password if supplied, and emits targeted diagnostic messages when offered methods do not match configured credentials.
- `open_or_create_path` is protected by `create_lock` so only the first parallel connection can create/truncate the remote file. After successful creation it sets global `create=false`.
- `.get_size` uses SFTP file attributes for regular files. For block devices, it binary-searches readable offsets because SFTP has no direct block-device size query.
- `.pread`/`.pwrite` implement positional I/O by `sftp_seek64` followed by sequential SFTP reads/writes. The thread model is `NBDKIT_THREAD_MODEL_SERIALIZE_REQUESTS` because seek plus read/write is not atomic per handle.
- `.pwrite` chunks writes to 128 KiB to avoid OpenSSH packet-size failure behavior.
- Flush and multi-conn are advertised only when the SFTP extension `fsync@openssh.com` version `1` is supported. `.flush` loops on `SSH_AGAIN`.

Important dependencies:
- libssh and SFTP APIs: `ssh_new`, `ssh_options_set`, `ssh_connect`, `ssh_userauth_*`, `sftp_*`.
- nbdkit plugin API and helpers: `nbdkit_parse_*`, `nbdkit_read_password`, `nbdkit_debug`, `nbdkit_error`.
- Utility headers: `array-size.h`, `cleanup.h`, `const-string-vector.h`, `minmax.h`.

Notes and risks:
- Multi-connection safety is inferred from OpenSSH fsync support; non-OpenSSH servers with that extension are treated as safe by proxy.
- Block-device sizing can be slow because it performs a binary search with remote reads.
- Reads do not explicitly handle `sftp_read` returning zero while `count > 0`; if a short/EOF read occurs unexpectedly, the loop may not progress.
- `create` is a global mutable flag, intentionally protected only around open/create so one plugin instance creates once.
