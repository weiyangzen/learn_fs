# File Research: sources/os/plan9/9front/sys/src/9/boot/bootrc

Main Plan 9 boot rc script for building the early namespace, selecting boot method, and starting init.

Key responsibilities:
- Creates `/n`, `/mnt`, and `/mnt/exportfs` mount generators.
- Binds core devices into `/dev` and network devices into `/net`.
- Imports RTC time and reparses selected environment variables.
- Prompts for `bootargs` unless suppressed.
- Starts factotum when needed and loads keys from secstore/auth.
- Runs boot method config/connect functions from `/rc/lib/*.rc`.
- Optionally inserts `cfs` into the boot service pipeline.
- Mounts root, overlays the selected root namespace, and execs architecture init.
- Starts keyboard and USB setup helpers.

Important behavior:
- Supports boot loop flattening through `#ec/bootloop`.
- Removes temporary boot environment and namespace pieces before `exec`.
- Loops after interrupted boot attempts, cleaning `/srv` state for retry.

Dependencies:
- Boot method rc libraries, factotum, secstore, cfs, mount services, namespace tools, `nusbrc`, and architecture `/init`.
