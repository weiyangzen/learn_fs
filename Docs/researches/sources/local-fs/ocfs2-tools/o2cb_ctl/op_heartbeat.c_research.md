# File Research: sources/local-fs/ocfs2-tools/o2cb_ctl/op_heartbeat.c

`o2cb` heartbeat-region configuration operations.

It accepts either a raw heartbeat region UUID/name or a block device. Block devices are opened as OCFS2 heartbeat-capable devices and converted to the filesystem UUID string. `add-heartbeat` inserts the region into a cluster, `remove-heartbeat` deletes it, and `heartbeat-mode` switches a cluster between `local` and `global`.
