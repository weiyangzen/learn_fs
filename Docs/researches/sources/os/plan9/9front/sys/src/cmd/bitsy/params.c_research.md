# File Research: sources/os/plan9/9front/sys/src/cmd/bitsy/params.c

This utility copies parameter data between a flash partition and `/tmp/tmpparams`.

Behavior:
- Default partition is `/dev/flash/user`, overrideable by positional argument.
- With `-f`, reads the flash partition and writes `/tmp/tmpparams`.
- Without `-f`, reads `/tmp/tmpparams`, erases the flash partition, and writes the data back.

Notable implementation details:
- `readfile` truncates at the first `0xff`, treating erased flash as terminator.
- `erase` writes `erase` to `<partition>ctl` if available.
- `writefile` creates missing destination files.

Risks and caveats:
- Silent returns on failed erase/write open paths can hide failure.
- Flash write path is destructive.
