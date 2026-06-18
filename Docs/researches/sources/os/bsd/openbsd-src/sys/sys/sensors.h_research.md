# File Research: sources/os/bsd/openbsd-src/sys/sys/sensors.h

Hardware sensor ABI and kernel sensor registry declarations.

This header defines the public sensor taxonomy used by OpenBSD `hw.sensors`: temperature, fan, voltage, power, current, capacity, drive state, timedelta, humidity, frequency, angle, distance, pressure, acceleration, velocity, and energy. User-visible `struct sensor` and `struct sensordev` expose descriptions, timestamps, values, type/status, per-type numbering, invalid/unknown flags, device names, and per-type maximum indices.

Under `_KERNEL`, it defines the kernel-side `ksensor` and `ksensordev` list structures plus registration, lookup, attach/detach, and periodic task APIs. The compatibility note is explicit: new fields should be appended to public structs.

Filesystem/storage relevance: not a filesystem header, but `SENSOR_DRIVE_*` states model disk/drive health and lifecycle, and `hw.sensors` is a common storage-monitoring surface for disk controllers and enclosure drivers.
