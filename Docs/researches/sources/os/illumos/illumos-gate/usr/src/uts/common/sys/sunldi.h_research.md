# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sunldi.h

`sunldi.h` declares the kernel Layered Driver Interface. Its opaque handle types represent layered-driver identities, open handles, callback registrations, and event cookies.

LDI events define success/failure/no-callback return values and event names for offline, degrade, and device removal. `ldi_ev_callback_t` version 1 carries notify and finalize callbacks, allowing a layered consumer to vote on or react to provider events.

Identity functions create/release an `ldi_ident_t` from anonymous context, module linkage, major number, devinfo node, device number, or STREAMS queue. Open functions create `ldi_handle_t` values by `dev_t`, path name, or devid/minor name, and helper functions return vnodes from path or devid. `ldi_close()` releases a handle.

The handle operation surface mirrors common driver entry points: read, write, ioctl, poll, get size, property operations, block strategy, dump, devmap, async read/write, STREAMS putmsg/getmsg, typed property lookups/getters, and queries for target dev_t, open type, devid, and minor name.

The event API lets consumers get event cookies, query event type strings, register/remove callbacks, and lets providers notify/finalize events for a devinfo/minor/spec-type tuple. This header is the public kernel-facing API; `sunldi_impl.h` defines the private backing structures.
