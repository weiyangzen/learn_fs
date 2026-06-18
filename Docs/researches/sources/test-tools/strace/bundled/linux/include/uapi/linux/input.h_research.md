# sources/test-tools/strace/bundled/linux/include/uapi/linux/input.h

Purpose: defines the Linux evdev userspace ABI consumed through `/dev/input/event*`, including event records, device identity, absolute axis metadata, keymap access, per-client event masks, and force-feedback effect payloads.

Important APIs/types/functions: `struct input_event`, `input_id`, `input_absinfo`, `input_keymap_entry`, `input_mask`, the `EVIOC*` ioctl macros, bus ID constants, multitouch tool constants, and the `ff_*` structures gathered by `struct ff_effect`. There are no functions; behavior is encoded as ioctl numbers and binary layout.

Control flow: user space reads streams of `input_event` records, then calls query/update ioctls for capabilities, absolute axes, keymaps, masks, grabs, clock selection, revoke, and force-feedback upload/removal. Time fields switch layout on 32-bit time64 builds.

State/persistence behavior: most queries are read-only device state. `EVIOCS*`, `EVIOCGRAB`, event masks, clock id, and force-feedback uploads mutate fd-local or device-driver state; event masks are explicitly per-client and force-feedback effect IDs persist until removed or the device/fd lifecycle ends.

Dependencies/integration: depends on `sys/time.h`, `sys/ioctl.h`, Linux integer types, and `input-event-codes.h`. strace should decode ioctl directions, variable-length bitmap/string ioctls, pointer-bearing `input_mask`, and union payloads in `ff_effect`.

Risks and test signals: ABI risk is high around time layout, packed fields, variable ioctl lengths, and userspace pointers such as `custom_data`. Tests should exercise EVIOCG/EVIOCS ioctl decoding, 32-bit compat layouts, force-feedback type unions, and masked event filtering semantics.
