# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_sensors.c

Purpose: Maintains kernel sensor device lists, sensor attachment numbering, lookup, periodic sensor task registration, and quiesce/restart behavior.

Key behavior:
- `sensordev_install()` inserts sensor devices into a sorted sparse-numbered global list and emits hotplug attach events.
- `sensor_attach()` inserts sensors per device, keeps sensors of the same type grouped, assigns per-type numbers, and updates `maxnumt`.
- `sensordev_deinstall()` and `sensor_detach()` remove devices/sensors and adjust counts.
- `sensordev_get()` and `sensor_find()` provide lookup by device number, type, and per-type sensor number.

Task model:
- `sensor_task_register()` creates or reuses the sensor task queue, allocates `sensor_task`, initializes timeout/task/rwlock, and starts the periodic cycle.
- `sensor_task_unregister()` marks tasks dead by setting period to zero under write lock.
- `sensor_task_tick()` queues work.
- `sensor_task_work()` runs the callback unless quiesced, frees dead tasks, or reschedules by period.

Concurrency:
- List mutations use `splhigh()`.
- Task lifetime is guarded by the task's rwlock plus deferred free from the worker.
- `sensor_quiesce()` waits for active sensor callbacks to drain; `sensor_restart()` clears the quiesced flag.

Filesystem relevance:
- No direct filesystem behavior. This is kernel device/sysctl support that may be observed through sensor sysctls allowed by pledge.
