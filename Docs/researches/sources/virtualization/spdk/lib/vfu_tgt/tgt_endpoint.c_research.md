# File Research: sources/virtualization/spdk/lib/vfu_tgt/tgt_endpoint.c

This file implements SPDK’s libvfio-user target endpoint manager. It registers endpoint device-type operations, creates vfio-user PCI endpoints, realizes PCI configuration and regions, attaches clients, handles DMA memory callbacks, and performs asynchronous endpoint shutdown on SPDK threads.

Global state includes the allowed target core mask, a mutex-protected endpoint list, a mutex-protected registered PCI device-ops list, the endpoint socket base path, and fini bookkeeping. `spdk_vfu_register_endpoint_ops()` installs one named `spdk_vfu_endpoint_ops` implementation, rejecting duplicates. `spdk_vfu_set_socket_path()` stores a base path and ensures it ends in `/`. `spdk_vfu_get_endpoint_by_name()` looks up live endpoints by name.

Each endpoint has an accept poller and a libvfio-user context poller. `tgt_accept_poller()` calls nonblocking `vfu_attach_ctx()` until a client connects, then calls the backend `attach_device()` hook and starts `tgt_vfu_ctx_poller()`. The context poller calls `vfu_run_ctx()` and handles `ENOTCONN` by unregistering itself, calling `detach_device()`, and marking the endpoint detached.

`tgt_endpoint_realize()` is the main construction path. It gets backend PCI device info, creates a libvfio-user socket context, configures logging, initializes PCIe config space, sets PCI IDs/class, adds vendor capabilities, adds PM/PCIe/MSI-X capabilities, configures each PCI region including sparse mmap descriptions and access callbacks, installs DMA add/remove callbacks, optional reset/quiesce callbacks, INTx/MSI-X irq counts, realizes the context, retrieves config-space and MSI-X capability pointers, and initializes selected config fields.

DMA callbacks register or unregister guest memory with SPDK only when the mapping is 2 MiB-aligned and read/write. Backend hooks `post_memory_add()` and `pre_memory_remove()` are called around SPDK memory registration/unregistration.

`vfu_parse_core_mask()` validates a requested endpoint cpumask is inside the global SPDK environment core mask and nonempty. `spdk_vfu_create_endpoint()` validates the endpoint name, rejects duplicates, finds a registered device type, builds the socket path, allocates and initializes endpoint private state through backend `init()`, realizes the endpoint, creates an SPDK thread, inserts the endpoint unless fini has started, and sends a message to start the accept poller on the endpoint thread.

Shutdown is asynchronous. `spdk_vfu_delete_endpoint()` removes the endpoint from the global list and sends `tgt_endpoint_thread_exit()` to its thread. That unregisters pollers, detaches the backend, destroys the libvfio-user context, then repeatedly calls backend `destruct()` until it no longer returns `-EAGAIN`. During global `spdk_vfu_fini()`, registered ops are freed, all endpoints are removed and asked to exit, and the fini callback runs after the last endpoint completes.

Accessor APIs expose endpoint id, name, libvfio-user context, private backend context, MSI-X/INTx state, PCI config pointer, and DMA map/unmap helpers. `spdk_vfu_map_one()` maps one guest address through `vfu_addr_to_sgl()` and `vfu_sgl_get()`, while `spdk_vfu_unmap_sg()` releases SGL mappings.

Key invariants are endpoint-list mutex protection, no endpoint creation after fini starts, backend hook ordering, libvfio-user context lifetime bound to endpoint thread shutdown, and 2 MiB alignment requirements before registering DMA memory with SPDK.
