# File Research: sources/os/plan9/plan9/sys/src/cmd/tarsplit/tarsplit.c

`tarsplit` splits a tar archive into independently readable tar archives under a configured maximum size.

Behavior:
- Default output prefix is `ts.` and default target size is `512*1024*1024`.
- `opennext` creates sequential output files named `<prefix><00000...>`, resets output offset with `newarch`, and reports the first/current member.
- `split` reads tar members with `getdir`, computes `header + rounded payload + end marker` size, closes the current output if the next member will not fit, and writes the member intact.
- A single member larger than the target size plus end overhead is fatal.

CLI:
- `-p pfx` chooses output prefix.
- `-s size` chooses max output size.
- Reads stdin or named input archives.

Dependencies:
- `tar.h` and `tarsub.c`.
