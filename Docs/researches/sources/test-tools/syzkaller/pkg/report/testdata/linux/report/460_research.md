# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/460

Purpose: golden fixture for warning parsing in input device registration. Expected title is `WARNING in input_register_device`, type is `WARNING`, and `PANICKED: Y`.

Important APIs, types, and functions: parser behavior includes warning-title extraction and panic-on-warn detection. Kernel frames include `add_uevent_var`, `__warn`, `report_bug`, `do_error_trap`, `input_register_device`-related USB/input device setup, `usb_set_configuration`, `usb_new_device`, and `hub_event`.

Control flow: a USB hub worker triggers a warning at `lib/kobject_uevent.c:670` and panic-on-warn follows immediately. The stack later reaches input registration during USB configuration. The parser should title the warning by the subsystem-level `input_register_device` rather than only `add_uevent_var`.

State and persistence behavior: static warning fixture with `PANICKED: Y`. It persists a long USB probe stack and warning panic tail.

Dependencies and integration points: depends on Linux warning report matching, panic-on-warn detection, and guilty-frame selection through device core/USB/input layers. Integrates USB input registration with kobject uevent warnings.

Risks: the first warning site is a generic kobject helper, so parser ranking is needed to preserve the expected input registration title. Immediate panic lines must not end extraction before the useful stack appears.

Test signals: `WARNING: CPU: 1 PID: 22 at lib/kobject_uevent.c:670 add_uevent_var`, `Kernel panic - not syncing: panic_on_warn set ...`, `Workqueue: usb_hub_wq hub_event`, `RIP: add_uevent_var`, and USB/input registration frames.
