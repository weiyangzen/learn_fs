# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbskel/usbskel.h

USB skeleton driver state header. It defines PM state and basic per-device skeleton state for a sample/teaching USB client driver.

`usbskel_power_t` tracks backpointer, supported power states, PM busy count, capabilities, raise-power flag, and current power. `usbskel_state_t` tracks devinfo, registration data, interrupt endpoint/pipe, device instance string, USB and driver state, mutex/CV serialization state, lock initialization, and PM pointer.

Constants cover open flag, max request size, device descriptor size, drain timeout, serialization modes, and logging destination flags.
