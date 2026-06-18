# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdjet.c

Defines a family of monochrome HP DeskJet, LaserJet, Kyocera FS-600, HP 2563B, and OCE 9050 printer devices.

The custom `gx_device_hpjet` extends printer state with `MediaPosition` and `ManualFeed` parameters plus “set” flags. Device descriptors include `deskjet`, `djet500`, `fs600`, `laserjet`, `ljetplus`, `ljet2p`, `ljet3`, `ljet3d`, `ljet4`, `ljet4d`, `lp2563`, and `oce9050`.

`hpjet_open` selects margins based on device family and paper size, enables duplex defaults for duplex models, and delegates to `gdev_prn_open`. `hpjet_close` emits final form/reset behavior, including odd duplex page ejection logic. `hpjet_make_init` injects paper tray/manual feed selection into page initialization strings.

Each `*_print_page_copies` routine supplies model-specific PCL initialization, resolution, and feature flags to `dljet_mono_print_page_copies` from `gdevdljm.c`. OCE output additionally switches between HPGL/2 and PCL modes.

Parameter handling exposes `ManualFeed` and reads `%MediaSource`, preserving values only after `gdev_prn_put_params` succeeds.

Risks: PCL command strings are device-specific and tightly coupled to feature flags. Init buffers are fixed-size but appear sized for local strings. Some devices leave margins to be filled dynamically, so open-time setup is required.
