# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kbtrans.h

## Role

`kbtrans.h` defines the interface between hardware keyboard drivers and the generic keyboard translation module. It keeps `struct kbtrans` and `struct kbtrans_hardware` opaque while exposing initialization, teardown, STREAMS message handling, key event delivery, LED handling, polled input, reset notification, queue management, and timeout cleanup APIs.

## Major Definitions

`KBTRANS_USBKB_DEFAULT_LAYOUT` indicates no kernel-configured USB keyboard layout, and `KBTRANS_KEYNUMS_MAX` is 255. `enum kbtrans_message_response` lets hardware drivers know whether `kbtrans` consumed a STREAMS message.

The callback surface is `struct kbtrans_callbacks`, with hardware callbacks for non-polled LED setting, polled LED setting, and polled key availability. `polled_keycode_func` and `struct hw_polledio` describe polled keycode retrieval state used by console/debugger paths.

## Interfaces

`kbtrans_streams_init()` initializes translation during the hardware driver's open path and returns opaque translation state; it accepts initial LED state/mask so firmware state such as NumLock can be preserved. `kbtrans_streams_fini()` tears it down. `kbtrans_streams_message()` processes upstream STREAMS messages and tells the hardware module whether more handling is needed.

Hardware drivers report actual key transitions through `kbtrans_streams_key()`, report keyboard type/table through `kbtrans_streams_set_keyboard()`, report resets through `kbtrans_streams_has_reset()`, and mark stream readiness with `kbtrans_streams_enable()`. Polled input uses `kbtrans_ischar()` and `kbtrans_getchar()`. Additional helpers update LED state, release all held keys, swap/get the upstream queue, and clear timeouts.

## Integration Notes

This header separates hardware scan-code delivery from generic keyboard translation and autorepeat. Hardware drivers are expected to suppress hardware-generated autorepeat and report only real press/release transitions. Polled routines are documented for single-threaded contexts such as kmdb/PROM input.
