# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hubd/hubdvar.h

Hub driver private state header. It defines hub power state, CPR callback state, main `hubd_t` soft state, hotplug/reset thread arguments, offline request records, init flags, child/port state flags, interrupt-pipe states, cfgadm states, power-budget constants, USB 3 route-depth limit, debug masks, and shared hubd interfaces.

`hubd_t` tracks device state, USBA device data, default and interrupt pipes, normalized hub characteristics, child devinfo and USBA device arrays, port change/reset/state/raw tracking, condition variables, NDI events, CPR callback, hotplug statistics, minor ancestry, cleanup/deathrow state, power budgeting, and optional child cleanup hook.

Concurrency is guarded by `h_mutex`, with Warlock annotations for hub and power data. The state diagram in comments documents transitions among online, disconnected, suspended, powered-down, recovery, and child power-level states.

This is the core hotplug, power-management, event, and cfgadm state contract for hubd.
