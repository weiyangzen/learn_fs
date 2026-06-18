<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsrahead/99-nfs.rules -->
# sources/user-network-fs/nfs-utils/tools/nfsrahead/99-nfs.rules

## Purpose

`99-nfs.rules` is the generated udev rule that invokes `nfsrahead` when a backing-device-info (`bdi`) device is added, then writes the program output into `read_ahead_kb`.

## Important APIs, Types, and Functions

The rule matches `SUBSYSTEM=="bdi"` and `ACTION=="add"`, runs `/usr/libexec/nfsrahead %k`, and assigns `ATTR{read_ahead_kb}="%c"` from the program's stdout.

## Control Flow

On bdi add events, udev calls the helper with the kernel device key. If the helper prints a value and exits successfully enough for udev assignment, the bdi readahead value is changed.

## State and Persistence Behavior

The rule itself is installed persistently under the udev rules directory. Runtime state is the kernel bdi `read_ahead_kb` attribute, which is not a config-file persistence layer.

## Dependencies and Integration Points

It depends on udev rule semantics, the installed `/usr/libexec/nfsrahead` path in this generated file, and sysfs bdi attributes. It integrates NFS mount detection with kernel readahead tuning.

## Risks and Edge Cases

The generated path can be wrong if install `libexecdir` differs from `/usr/libexec` without regeneration. Helper latency can block udev event processing, which is why the C helper contains mountinfo wait limits and fast non-NFS rejection.

## Test Signals

Packaging tests should verify the installed rule path matches the installed helper path, and udev integration tests should simulate bdi add events for NFS and non-NFS device numbers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsrahead/99-nfs.rules -->
