# File Research: sources/os/plan9/9front/sys/src/cmd/venti/words/wrtape

`wrtape` is an rc backup script that selects a tape number’s 32-arena batch from the Venti HTTP index, logs each arena to `/sys/log/ventibackup`, and writes each arena stream from `venti/rdarena` to a SCSI tape device with filemarks.

It depends on site-specific host `iolaire`, `/dev/sd03`, `scuzz`, `hoc`, `hget`, and HTTP index formatting. It is operational backup glue rather than portable tooling.
