# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_sensors.c

This file implements DragonFlyBSD's hardware sensor registry, sysctl exposure, and periodic sensor task scheduler. It is derived from OpenBSD sensor infrastructure.

Sensor registry:
- `sensordev_list` stores installed sensor devices with stable numeric IDs.
- `sensordev_install()` inserts a device at the first available numeric slot, updates `sensordev_idmax`, and installs its sysctl node.
- `sensor_attach()` inserts a sensor into the device's sensor list, keeps sensors of the same type grouped, assigns `numt`, updates per-type counts, and installs the sensor sysctl.
- `sensor_detach()` and `sensordev_deinstall()` remove sensors/devices and deinstall sysctl nodes.
- `sensordev_get()` and `sensor_find()` resolve MIB-style lookups while the sysctl lock is held.

Sensor task scheduler:
- `struct sensor_task` stores callback, argument, period, next-run time, running flag, CPU, and queue link.
- `sensor_task_threads[MAXCPU]` maintains one task list and lock per CPU.
- `sensor_task_register()` registers on the default CPU; `sensor_task_register2()` allows CPU selection.
- `sensor_task_unregister()` and `sensor_task_unregister2()` mark tasks not running; the scheduler thread later frees inactive tasks.
- `sensor_task_thread()` sleeps until tasks are due, removes due tasks, runs callbacks, and reschedules still-running tasks in next-run order.
- `sensor_sysinit()` chooses a default CPU near package 0 when topology data exists, initializes per-CPU queues/locks, and starts a `sensors N` kernel thread on each CPU.

Sysctl surface:
- Exposes `hw.sensors`, `hw._sensors`, and `hw.sensors.dev_idmax`.
- `sensordev_sysctl_install()` creates a per-device sysctl node and installs children for already attached sensors.
- `sensor_sysctl_install()` creates read-only per-sensor `CTLTYPE_STRUCT` nodes.
- `sysctl_handle_sensordev()` and `sysctl_handle_sensor()` copy kernel structures into sanitized user-visible structures without kernel pointers.
- `sysctl_sensors_handler()` implements the numeric MIB interface for device or sensor lookup.

Concurrency:
- Device/sensor registry changes occur under `SYSCTL_XLOCK()`.
- Sensor task queues use per-CPU `struct lock` locks.

Filesystem/storage relevance:
- Not directly filesystem code, but sensor data can feed storage/thermal monitoring and platform health decisions around disks and controllers.
