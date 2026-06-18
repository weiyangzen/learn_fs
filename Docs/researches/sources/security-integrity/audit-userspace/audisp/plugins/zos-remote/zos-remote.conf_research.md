# sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/zos-remote.conf

Purpose: Sample/default configuration for the z/OS remote audit dispatcher plugin.

Important settings: Defines `server`, `port`, `user`, `password`, `timeout`, and `q_depth`. These correspond to the plugin config consumed by `plugin_load_config()` in `zos-remote-plugin.c`.

Control flow: The file has no executable flow. At runtime, `zos-remote-plugin.c` reads a config file at startup and after SIGHUP, then passes server/session settings to `zos_remote_init()` and queue depth to `increase_queue_depth()`.

State and persistence: This is persistent on-disk configuration. The sample contains placeholder credentials (`RACF_ID`, `racf_password`) and a default LDAP port (`389`).

Dependencies and integration points: Integrated with the z/OS remote config parser and indirectly with the plugin submit thread, LDAP server connection, and queue allocation.

Risks and edge cases: The config includes a plaintext password field. Deployments need file permissions and secret handling guidance. If `q_depth` is too small, events may be dropped by the plugin's queue; if too large, memory use rises. The sample uses unencrypted LDAP port 389 unless the surrounding z/OS remote LDAP layer applies security elsewhere.

Test signals: Config parser tests should confirm all keys parse, defaults apply when omitted, invalid numeric values fail, and SIGHUP reload grows the queue without losing pending BERs.
