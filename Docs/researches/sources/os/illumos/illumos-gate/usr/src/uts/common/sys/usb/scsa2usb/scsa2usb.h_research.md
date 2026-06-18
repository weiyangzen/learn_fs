# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/scsa2usb/scsa2usb.h

USB mass-storage SCSI bridge private header. It defines device limits, transfer limits, many vendor/product quirk IDs, quirk attribute flags, power state, last-command tracking, configuration overrides, main `scsa2usb_state_t`, command protocol flags, state macros, SCSA conversion macros, auto-request-sense helpers, CPR callback state, per-command state, CDB field extraction helpers, READ CAPACITY layout, CD block-size helpers, debug masks, and minor-number mapping for ugen support.

`scsa2usb_state_t` is the main per-device object: it tracks USB/SCSI state, transport ownership, mutex/cv, SCSI transport and current packet, per-LUN wait queues/inquiry/devinfo/capacity, endpoint descriptors and pipe handles, packet/pipe state, max HCD bulk transfer, command protocol, work thread, override state, warning suppression, not-ready state, ugen handle, and clone minors.

The header is heavily compatibility-oriented. Quirk flags handle broken GET_MAX_LUN, power management, START_STOP, MODE SENSE, INQUIRY, CSW residue, media checks, and capacity adjustment behavior.

Correctness concerns include command serialization, reset/busy state tests, CDB byte extraction, transfer-size limits, and avoiding repeated timeout-heavy commands for known broken firmware devices.
