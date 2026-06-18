# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usba_types.h

## Role

Defines the core private USBA data model for pipe handles, USB devices, event registrations, endpoint indexing, speeds, and serialization.

## Key Interfaces

- `usba_ph_impl_t` backs opaque pipe handles and stores mutex, pipe data pointer, owner dip, endpoint descriptor, pipe policy, flags, refcount, pipe state, and state-changing flag.
- `usba_pipe_handle_data_t` stores per-open-pipe state: request queue, shared device pointer, pipe policy, standard and extended endpoint descriptors, owner dip, mutex, HCD/client private pointers, request count, task queue, callback queue, soft interrupt count, and special flags.
- Defines default pipe index, pipe-closing checks, default-pipe detection, endpoint count, PM component count, speed constants, port types, and data-toggle/persistent flags.
- `usba_evdata_t` stores per-devinfo event callback IDs for removal, insertion, suspend, and resume.
- `usb_client_dev_data_list_t` links multiple client registration data instances for one device.
- `usba_device_t` represents a USB device shared by multiple devinfo/client nodes. It stores device pipe list, mutex, dip, HCD ops, hub pointer, USB address, root hub fields, descriptors, raw/current/all configuration data, strings, preferred driver, port status, high-speed hub transaction state, hub bandwidth data, power draw, refcount, allocated request tracking, event cookies, client cleanup lists, shared task queues, parent hub pointer, HCD private pointer, and parsed BOS data.
- Defines client cleanup flags.
- `usba_serialization_impl_t` backs the public USB serialization handle.

## Design Notes

The comments emphasize that `usba_device_t` can be shared by multiple clients or devinfo nodes for composite devices. Pipe handles are unique even when underlying pipes can be shared.

## Risk Notes

This is high-risk shared state. Endpoint indexing assumes 32 endpoints and bitmask-sized exclusive tracking. Incorrect locking or lifetime handling can break composite devices, event callbacks, shared task queues, or HCD private state.
