# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/459

Purpose: golden fixture for a page fault during USB HID/input device removal. Expected title is `BUG: unable to handle kernel paging request in input_unregister_device`, alternate title is `bad-access in input_unregister_device`, type is `MEMORY_SAFETY_BUG`, and `PANICKED: Y`.

Important APIs, types, and functions: parser behavior includes page-fault classification, bad-access alternate creation, and panic detection. Kernel frames include `kobject_put`, `device_del`, `input_unregister_device`, `hidinput_disconnect`, `hid_disconnect`, `hid_hw_stop`, `ms_remove`, `hid_device_remove`, and USB hub workqueue handling.

Control flow: a `usb_hub_wq hub_event` worker faults in `kobject_put`; the stack identifies the higher-level input unregister path during HID disconnect. The parser must prefer `input_unregister_device` over the generic `kobject_put` top frame and handle an interleaved raw-gadget failure message.

State and persistence behavior: static fixture with fatal-exception panic state. It persists teardown ordering and repeated RIP/register sections but no mutable test state.

Dependencies and integration points: depends on Linux page-fault oops parsing, stack guilty-frame ranking, panic detection, and workqueue context handling. Integrates USB HID, input, device core, and raw gadget noise into parser coverage.

Risks: generic device-core frames can hide the subsystem-specific cause. Interleaved `raw_ioctl_run` text can break report body extraction if boundaries are too strict.

Test signals: `BUG: unable to handle page fault`, `Workqueue: usb_hub_wq hub_event`, `RIP: kobject_put`, stack `device_del -> input_unregister_device -> hidinput_disconnect`, and fatal-exception panic.
