# File Research: sources/os/plan9/9front/sys/src/cmd/aux/acpi.c

ACPI service that reads ACPI tables, evaluates AML, exposes battery/CPU temperature/power controls through a 9P filesystem, and can power off the machine.

Important behavior:
- Opens `/dev/ec`, `/dev/acpimem`, `/dev/iob`, `/dev/iow`, `/dev/iol`, and `/dev/acpitbls`, falling back to `#P/...`.
- Loads DSDT/SSDT AML tables; parses FACP/FADT register locations for PM1 and GPE controls.
- Enumerates embedded controllers, batteries (`_BIF`/`_BST`), and thermal zones associated with CPUs (`_PSL`/`_TMP`).
- Creates a 9P tree mounted by default at `/dev` with files:
  - `battery`: percentage, units, capacities, voltage, time estimate, state.
  - `cputemp`: CPU thermal readings.
  - `pmctl`: writable control file.
- Writing `power off` to `pmctl` calls `_PTS`/`_TTS`, disables GPEs, and writes sleep type/enable to PM1 control registers for S5.
- `-H` attempts immediate halt/poweroff; `-D` enables 9P chatty mode; `-p` enables AML debug.

Filesystem relevance:
- Implements a synthetic 9P device filesystem over ACPI state and control.
- Bridges kernel device files, AML evaluation, and user-facing power-management files.
