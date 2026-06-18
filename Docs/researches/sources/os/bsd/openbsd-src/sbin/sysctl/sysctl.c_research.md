# File Research: sources/os/bsd/openbsd-src/sbin/sysctl/sysctl.c

Large command-line implementation of OpenBSD `sysctl`: resolves textual MIB names, lists known variables, reads values, writes new values, and formats special kernel structures.

Top-level flow:
- Options: `-A`, `-a`, `-f file`, `-n`, `-q`, and compatibility `-w`.
- Uses `unveil()` to restrict access to `_PATH_DEVDB`, `/dev`, and optional config file.
- With no arguments or `-A/-a`, initializes dynamic debug and VFS names, then lists all known sysctl names.
- With `-f`, reads config lines, strips whitespace/comments, and parses each assignment.
- Each CLI/config token is processed by `parse()`.

Name resolution:
- `struct ctlname` arrays from kernel headers define top, kern, vm, net, hw, machdep, ddb, and nested names.
- `struct list` pairs name arrays with max IDs.
- `findname()` consumes dot-separated components with `strsep()`.
- `listall()` recursively emits known variables under a prefix.
- Dynamic tables:
  - `debuginit()` populates `debug.*` names via `CTL_DEBUG_NAME`.
  - `vfsinit()` queries `CTL_VFS.VFS_GENERIC.VFS_MAXTYPENUM` and `VFS_CONF`, building runtime filesystem names and mapping FFS/NFS/FUSEFS subtrees.

Value parsing and writing:
- `name=value` implies write; `-w` is no longer required.
- Converts integers with `strtonum()`, quads with `sscanf()`, and selected strings from hex.
- `parse_hex_string()` supports fixed binary sysctl string inputs.
- `parse_baddynamic()` edits TCP/UDP bad dynamic/root-only port bitmaps, supporting full lists and `+`/`-` incremental ranges.

Special formatting:
- Clock and boottime structures.
- Character/block device names through `devname()`.
- BIOS geometry/device values when available.
- Unsigned integer output.
- Kernel malloc buckets/stats.
- Long arrays such as CPU time.
- Sensors with typed unit formatting and status.
- Timeout statistics.
- Hex values for selected machdep fields.

Subsystem handlers:
- Kernel: profiling, fork stats, tty stats, name cache stats, malloc stats, sem/shm info, watchdog, timecounter, audio, video, witness, timeout stats.
- VM: load average, ps strings, swap encryption, and selected tunables; redirects many stats to `vmstat`/`systat`.
- Net: IPv4 protocol variables, IPv6 protocol variables, Unix socket variables, link variables, BPF, MPLS, PIPEX; redirects bulk protocol stats to `netstat`.
- VFS: generic filesystem instance listing plus FFS/NFS/FUSEFS variable resolution.
- HW: sensors, battery, and selected memory/smt behavior.
- Machdep: console device, CPU feature hex strings, block/char conversions, BIOS, chipset if compiled in.

Sensor handling:
- `sysctl_sensors()` can list all sensor devices, list all sensors on one device, list one sensor type, or resolve a specific sensor index.
- `print_sensor()` formats temperature, fan RPM, volts, ohms, watts, amps, energy, humidity, frequency, angle, distance, pressure, acceleration, velocity, drive state, indicator, percent, integer, and timestamps.

Filesystem/storage relevance:
- Important VFS/storage administration surface. It dynamically discovers mounted filesystem types, exposes FFS/NFS/FUSEFS sysctl branches, redirects specialized filesystem/network stats to dedicated tools, and formats kernel-facing values used by OS diagnostics.
