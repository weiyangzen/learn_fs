# File Research: sources/virtualization/nvme-cli/plugins/sed/sed.c

CLI wrapper layer for the SED Opal plugin. It parses nvme-cli options, opens the target NVMe namespace device, and delegates to `sedopal_cmd.c` implementation functions.

Commands:
- `sed_opal_discover`: query and display locking features.
- `sed_opal_initialize`: initialize an Opal device for locking.
- `sed_opal_revert`: revert from locking state; supports destructive and PSID flags.
- `sed_opal_lock`: lock the global locking range.
- `sed_opal_unlock`: unlock, optionally read-only.
- `sed_opal_password`: change the locking password.

Important behavior:
- `sed_opal_open_device` requires a namespace handle, not a controller handle. It emits an explicit error if invoked on `/dev/nvmeX` instead of `/dev/nvmeXnY`.
- Option variables are globals declared in `sedopal_cmd.c`; CLI option parsing mutates those globals directly.
- `--ask-key`, `--read-only`, `--destructive`, `--psid`, `--verbose`, and `--udev` control behavior in lower layers.

Storage relevance:
- This plugin manipulates block-layer OPAL locking state, which directly affects namespace accessibility, partition rereads, and mounted filesystem usability.
