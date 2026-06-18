# File Research: sources/virtualization/qemu/hw/virtio/virtio-input-pci.c

Defines the common virtio-input PCI base type and concrete PCI wrappers for keyboard, mouse, tablet, and multitouch virtio input devices.

Key entry points:
- `virtio_input_pci_realize()` forces virtio 1.0 mode and realizes the embedded `VirtIOInput` device on the proxy bus.
- `virtio_input_pci_class_init()` installs the default `vectors=2` property, assigns the realize hook, marks the device as input-category, and sets PCI class `PCI_CLASS_INPUT_OTHER`.
- HID-specific class initializers set keyboard and mouse PCI subclass IDs.
- `virtio_keyboard_initfn()`, `virtio_mouse_initfn()`, `virtio_tablet_initfn()`, and `virtio_multitouch_initfn()` initialize embedded `VirtIOInputHID` devices with their concrete virtio input type.
- `virtio_pci_input_register()` registers abstract base types and concrete PCI device types.

Core mechanics:
- `TYPE_VIRTIO_INPUT_PCI` is abstract and extends `TYPE_VIRTIO_PCI`.
- `TYPE_VIRTIO_INPUT_HID_PCI` is an abstract HID PCI layer for concrete HID-like input devices.
- Concrete generic PCI names are `virtio-keyboard-pci`, `virtio-mouse-pci`, `virtio-tablet-pci`, and `virtio-multitouch-pci`.
- All concrete wrappers delegate actual input protocol behavior to the embedded virtio input core device.

Important invariants:
- Virtio-input PCI is always forced to virtio 1.0 mode.
- The default vector count is 2.
- The concrete wrapper's embedded `vdev` type must match the advertised generic PCI name.

Filesystem/block relevance:
- No filesystem or block behavior. This is a virtio PCI transport binding pattern used elsewhere in QEMU.

Notable risks:
- PCI class IDs affect guest driver matching and device categorization.
- The file depends on `virtio_instance_init_common()` to correctly bind wrapper lifetime to the embedded virtio device.
