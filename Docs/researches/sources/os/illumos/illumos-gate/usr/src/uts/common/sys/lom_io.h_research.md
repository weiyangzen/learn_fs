# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lom_io.h

## Role

LOMlite/TSalarm/BSCV user-kernel ioctl ABI header for platform alarm, watchdog, event log, LED, voltage, temperature, serial, and field-programming controls.

## Structure

- Defines TSalarm monitor/control ioctls and small alarm/watchdog/debug structures.
- Defines LOMlite legacy aliases and newer monitor/control ioctls for PSU, event log, fan, fault LED, info, control, programming, daemon/debug monitor, GPIO inputs, manufacturing programming, and LED state.
- Defines fixed-size data structures for alarm, watchdog, PSU, fan, event log, LED state, info, control, manufacturing/programming buffers, and LOMlite2 extensions.
- Defines event-code constants and encoding macros for fault LED, alarm, fan, and PSU events.
- Defines LOMlite2 ioctls/structures for serial event control, voltages, status flags, temperatures, console buffer, extended event log, extended info, test commands, manufacturing read/write, sleep, and lomp field-programming controls.

## Dependencies And Consumers

Includes `sys/ioccom.h` for ioctl encoding macros. Consumers are LOM/BSCV platform drivers and management utilities that pass the fixed-size structures across ioctl boundaries.

## Important Details

Many structs use fixed array limits (`MAX_PSUS`, `MAX_FANS`, `MAX_EVENTS`, `MAX_EVENT_STR`, etc.) that are part of the ABI. Event encoding macros do not validate alarm/fan/PSU numbers beyond masking low status bits, so callers/drivers must validate ranges.

## Research Notes

Read completely: 633 lines, 14574 bytes.
