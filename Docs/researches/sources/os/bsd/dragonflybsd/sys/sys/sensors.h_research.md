# File Research: sources/os/bsd/dragonflybsd/sys/sys/sensors.h

This header defines the OpenBSD-derived hardware sensor ABI and DragonFly kernel sensor registration/task interface.

Key responsibilities:
- Defines `enum sensor_type` for temperature, fan, voltage, resistance, power, current, capacity, boolean indicators, raw integers, percent, illuminance, drive state, timedelta, ECC, frequency, and reserved types.
- Provides `sensor_type_s[]` string names for all sensor types plus `undefined`.
- Defines drive-state values such as empty, ready, online, idle, active, rebuild, powerdown, fail, and predictive fail.
- Defines `enum sensor_status`:
  - unspecified
  - OK
  - warning
  - critical
  - unknown
- Defines user-visible `struct sensor`:
  - description
  - last-change timeval
  - value
  - type/status
  - per-type number
  - flags
- Defines sensor flags:
  - `SENSOR_FINVALID`
  - `SENSOR_FUNKNOWN`
- Defines user-visible `struct sensordev` and `MAXSENSORDEVICES`.
- In kernel builds, defines:
  - `struct ksensor`
  - `struct ksensordev`
  - sensor device/sensor list links
  - sysctl nodes and contexts
- Declares kernel install/deinstall and attach/detach APIs.
- Declares deprecated `sensor_task_register()`/`sensor_task_unregister()` and replacement `sensor_task_register2()`/`sensor_task_unregister2()`.
- Defines inline helpers:
  - `sensor_set_invalid()`
  - `sensor_set_unknown()`
  - `sensor_set()`
  - `sensor_set_temp_degc()`

Important invariants:
- Public structures note that new fields should be appended for backward compatibility.
- Temperature values are represented in microkelvin; `sensor_set_temp_degc()` converts Celsius to microkelvin using `degc * 1000000 + 273150000`.
- Kernel `ksensor` mirrors the public sensor fields and adds list/sysctl linkage.

Research notes:
- This is both the user-visible sensor reporting schema and the kernel provider registration surface.
