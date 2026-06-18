# sources/test-tools/stress-ng/core-vmstat.h

## Purpose
`core-vmstat.h` exposes the VM/statistics reporter lifecycle and mount-device lookup API.

## Important APIs, Types, And Functions
It declares `stress_find_mount_dev`, `stress_vmstat_start`, and `stress_vmstat_stop`. The start/stop calls are used to manage the periodic stats child process.

## Control Flow
Callers start the stats reporter after options and shared state are initialized, then stop it during shutdown. `stress_find_mount_dev` can be called independently to map a path to its backing device.

## State And Persistence
The header declares no state. Implementation state includes reporter PID, delay settings, counter baselines, and output streams.

## Dependencies And Integration Points
It includes `core-attribute.h` for return attributes and relies on common declarations from the broader stress-ng include environment. It integrates with command-line option handling and global run lifecycle.

## Risks
Callers must avoid double-starting without stopping, because `core-vmstat.c` tracks only one static child PID. Device lookup returns static storage on supported platforms, so callers must copy results if they need stable values across later calls.

## Test Signals
Build coverage validates prototypes. Runtime validation comes from `--vmstat`, `--iostat`, and coverage-script runs that require the stats process to start and stop cleanly.
