# File Research: sources/os/plan9/plan9/sys/src/9/port/devdup.c

Implements `#d`, the per-process file-descriptor duplication namespace. Each open fd appears as `<fd>`, and each control view appears as `<fd>ctl`; qid path encoding is `2*fd + isctl + 1`.

`dupgen` enumerates the current process `fgrp`, derives permissions from the underlying channel mode for data files, and gives ctl files read permission. Opening a data entry returns the underlying channel via `fdtochan`; the original device channel is closed. Opening a ctl entry opens the synthetic ctl file itself.

Reading a ctl entry formats fd metadata with `procfdprint`, matching `/proc/*/fd` style output. Data entries are not read through this device after open because opening them hands back the real channel.

The device has no write support. It depends directly on `up->fgrp`, `fdtochan`, and `procfdprint`, and is mainly a lightweight fd-to-file namespace adapter.
