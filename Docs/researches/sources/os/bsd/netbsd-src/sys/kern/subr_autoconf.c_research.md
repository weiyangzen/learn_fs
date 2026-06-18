# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_autoconf.c

Read completely: 4041 lines.

Implements NetBSD's machine-independent device autoconfiguration core. It manages configured driver/attachment/cfdata tables, device allocation and naming, matching and attachment, deferred configuration queues, detach/shutdown/deactivation, device lookup and lifetime references, compatible-string matching, power-management registration and locking, activity handlers, and safe iteration over the live device tree.

Global configuration state:
- Static ioconf exports `cfdata` and `cfroots`; the file keeps all loaded cfdata tables in `allcftables`.
- `allcfdrivers` tracks all registered `cfdriver` structures, and `allcfattachiattrs` tracks rare attachment-provided interface attributes.
- `alldevs` is the global device list guarded by `alldevs_lock`, with generation counters and reader/writer counters to support iteration while detaching.
- `config_misc_lock` and `config_misc_cv` protect pending attach/detach state, deferred queues, and device reference draining.
- Autoconfiguration timings are mixed into the entropy pool through `rnd_autoconf_source`.

Driver, attachment, and cfdata management:
- `config_init()` initializes locks, callouts, built-in drivers and attachments, the initial cfdata table, and the autoconf entropy source.
- `config_init_component()` and `config_fini_component()` add/remove module-provided driver, attachment, and cfdata sets with rollback on failure.
- `config_cfdriver_attach()` rejects duplicate driver names and inserts into `allcfdrivers`; `config_cfdriver_detach()` refuses removal while instances or attachments remain.
- `config_cfattach_attach_iattrs()` attaches a `cfattach` to a driver and records its interface attributes; detach refuses removal while any live device uses the attachment.
- `config_cfdata_attach()` adds supplemental cfdata and optionally rescans existing parents; `config_cfdata_detach()` detaches all devices backed by that cfdata before removing it.

Matching and searching:
- `config_match()` and `config_probe()` invoke a candidate attachment's match routine.
- `config_stdsubmatch()` compares locators for an interface attribute before calling `config_match()`.
- `cfdriver_get_iattr()`, `cfattach_get_iattr()`, `device_get_iattr()`, and `cfiattr_lookup()` resolve interface attribute descriptors.
- `cfparent_match()` verifies that a candidate parent device supports the required interface attribute and optional specific parent name/unit.
- `config_search_internal()` scans all cfdata tables for eligible children, filters by found-state and interface attribute, invokes submatch/default match, and returns the best-priority candidate.
- `config_rootsearch()` searches root cfdata entries from `cfroots`.

Attachment and device allocation:
- `cfargs_canonicalize()` validates and normalizes `struct cfargs`, enforcing mutually exclusive submatch/search callbacks.
- `config_devalloc()` allocates the device structure and driver private storage, assigns a unit, builds `dv_xname`, initializes the PMF lock/CV, copies locators, creates the property dictionary, initializes localcount references, and records interface attributes in properties.
- `config_unit_alloc()` uses `config_makeroom()` to grow `cd_devs` arrays as needed under the global device lock.
- `config_attach_internal()` links the device, marks cfdata found, prints attach messages, registers the device, sends devmon attach events, prevents detach during attach/deferred work, calls the driver's attach routine, clears `dv_attaching`, runs deferred config for the parent, and returns a referenced device.
- `config_found_acquire()`, `config_attach_acquire()`, and `config_attach_pseudo_acquire()` are reference-returning APIs; legacy `config_found()`, `config_attach()`, and `config_attach_pseudo()` immediately release the returned reference.
- `config_rootfound()` attaches root devices.

Deferred and final configuration:
- `config_defer()` queues callbacks until the parent finishes attaching all children.
- `config_interrupts()` queues callbacks until interrupts are enabled, with worker threads created by `config_create_interruptthreads()`.
- `config_mountroot()` queues callbacks until after root mount, with joinable mountroot threads created/finalized by `config_create_mountrootthreads()` and `config_finalize_mountroot()`.
- `config_pending_incr()` and `config_pending_decr()` maintain per-device pending counters and the global pending list.
- `config_finalize_register()` stores iterative finalizers until finalization; if finalization already happened it runs the callback immediately until it makes no more progress.
- `config_finalize()` waits for pending deferred work, attaches pseudo-devices, runs finalizers to quiescence, releases finalizer records, handles boot twiddle state, and reports hardware detection errors.

Detach, shutdown, and deactivation:
- `config_detach_enter()` waits for attach/deferred work and any competing detach, then marks the current LWP as detaching.
- `config_detach_release()` calls the driver's detach routine, handles forced-detach panic semantics, commits detach if the driver did not, clears active state, drains `device_lookup_acquire()` references, notifies userland, checks for children under DIAGNOSTIC, notifies the parent, updates cfdata found-state, and unlinks or garbage-marks the device.
- `config_detach_commit()` is an idempotent signal from a driver detach routine that future device lookups should fail promptly.
- `config_detach_children()` detaches direct children.
- `config_detach_all()` iterates active devices leaves-first for shutdown unless reboot flags skip detach.
- `config_deactivate()` walks descendants root-first and invokes `ca_activate(..., DVACT_DEACTIVATE)` under `splhigh()`.
- `config_collect_garbage()` and `config_dump_garbage()` defer actual device memory destruction until no readers/writers are iterating the device list.

Device lookup, references, and iteration:
- `device_lookup()` is non-sleeping and safe up to IPL_VM, but returns an unreferenced device that callers must know is stable.
- `device_lookup_acquire()` sleeps until attach/detach state stabilizes and returns a reference acquired through `localcount`.
- `device_acquire()` and `device_release()` manage per-device localcount references.
- `device_find_by_xname()` and `device_find_by_driver_unit()` search by external name or driver/unit.
- `deviter_init()`, `deviter_next()`, and `deviter_release()` provide generation-based iteration over devices, supporting normal, read-write, shutdown, root-first, and leaves-first traversal modes.
- Iterators maintain `alldevs_nread`/`alldevs_nwrite` to prevent immediate reclamation of detached device structures.

Compatible matching:
- String-array helpers implement exact and `pmatch(9)` pattern matching.
- `device_compatible_match()` and `device_compatible_pmatch()` rank matches by the position of the matched device compatible string.
- String-list variants support OpenFirmware-style NUL-separated compatible lists.
- ID variants match integer IDs against `device_compatible_entry` arrays with a sentinel.
- Lookup variants return the matching `device_compatible_entry` rather than just a score.

Power management and activity:
- Driver, bus, and class PMF registration stores suspend/resume/shutdown callbacks and private data on the device.
- Suspend/resume is layered: class, driver, and bus flags gate each other so deeper layers suspend/resume in the intended order.
- `device_pmf_lock()`/`device_pmf_unlock()` serialize PMF operations, allow recursive locking by the same LWP, and wake waiters during deregistration.
- `device_pmf_driver_deregister()` clears power handler state and waits until outstanding PMF locks/waiters drain.
- Activity handlers can be dynamically registered and deregistered; `device_active()` invokes them for device activity events.

Userland and sysctl integration:
- `devmon_report_device()` emits property-dictionary attach/detach events through `devmon_insert_vec` when drvctl/devmon is present.
- Device property dictionaries include driver, unit, parent, and interface attribute locator descriptions.
- `sysctl_detach_setup()` creates writable `kern.detachall` to control shutdown detach behavior.
- Boot `twiddle` support provides progress feedback for silent boot modes.

Risks and notes:
- Device lifetime is subtle: legacy APIs return unreferenced `device_t` values and rely on the kernel lock as a fragile race defense, while newer acquire APIs require explicit `device_release()`.
- Comments explicitly note that not all detach callers hold the iterator/read-write protection needed to avoid use-after-free races.
- `config_makeroom()` drops and reacquires `alldevs_lock` around sleeping allocation; callers must re-check state after it returns.
- Forced detach panics if a driver refuses or fails detach, so driver detach callbacks must distinguish removable-hardware force paths carefully.
- PMF deregistration intentionally wakes and waits on PMF lock holders; incorrect lock ordering around device PMF locks can deadlock suspend/resume paths.
- `device_pmf_driver_shutdown()` and `device_pmf_bus_shutdown()` dereference function pointer slots in a way that assumes callback storage is initialized consistently.
