# File Research: sources/os/bsd/netbsd-src/sys/sys/envsys.h

Defines ENVSYS 2 environmental sensor units, states, ioctls, and legacy compatibility structures.

Key content:
- Limits: `ENVSYS_MAXSENSORS`, `ENVSYS_DESCLEN`.
- Sensor units: temperature, fan RPM, AC/DC volts, ohms, watts, amps, watt/amp hours, indicator, integer, drive, battery capacity/charge, humidity, lux, pressure.
- Sensor states: valid, invalid, critical, warn/critical under/over.
- Drive state enum and legacy drive state macros.
- Battery capacity and indicator states.
- Dictionary ioctls: get/set/remove properties.
- Legacy `envsys_tre_data_t` with current/min/max/avg data, warning flags, valid flags, units.
- Warning and valid flag constants.
- Legacy `envsys_basic_info_t` and `ENVSYS_GTREINFO`.
- Optional unit/status name arrays under `ENVSYSUNITNAMES`.

Important behavior:
- Modern interface is proplib dictionary based.
- Compatibility keeps old envsys ioctl consumers working for data/info reads.
