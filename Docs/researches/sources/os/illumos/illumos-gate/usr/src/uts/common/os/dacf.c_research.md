# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/dacf.c

## Purpose

`dacf.c` implements the core Device Autoconfiguration Framework. DACF is a lightweight policy engine that maps device descriptions and kernel lifecycle actions to configuration operations supplied by kernel modules.

The rule database maps:

`(device specifier, DACF operation) -> (module, opset, op args, options)`

Supported operations in this file are `post-attach` and `pre-detach`. Supported device specifiers are `minor-nodetype`, `driver-minorname`, and `device-path`.

## Initialization And Rule Storage

`dacf_init()` creates the rule hash matrix, module hash, and per-minor info hash. It registers the synthetic `__kernel` DACF module and reads `/etc/dacf.conf` through `read_dacf_binding_file(NULL)`.

Rules are stored in operation/specifier-specific hash tables selected through `dacf_rule_matrix`. Each hash uses the rule’s device spec string as key and a `dacf_rule_t` as value. Rule values own the key string, so the hash uses a null key destructor and `dacf_rule_val_dtor()` releases the rule.

`dacf_clear_rules()` clears all rule hashes, typically before rereading configuration.

## Rule Lifecycle

`dacf_rule_insert()` validates the requested operation/specifier pairing, constructs a rule with `dacf_rule_ctor()`, takes an initial reference, and inserts it into the proper hash. Duplicate rules are rejected.

`dacf_rule_ctor()` copies the device spec, module name, opset name, options, operation ID, and argument list. A null module name is normalized to `__kernel`.

Rules are reference-counted under `dacf_lock`:

- `dacf_rule_hold()` increments `r_refs`.
- `dacf_rule_rele()` decrements and destroys at zero.
- `dacf_rule_destroy()` frees copied strings and argument lists.

Arguments are maintained as linked `dacf_arg_t` entries with duplicate-name rejection in `dacf_arg_insert()` and full teardown in `dacf_arglist_delete()`.

## Reservations

Reservations defer matched operations until a lifecycle point. `dacf_rsrv_make()` attaches a rule and info handle to a `dacf_rsrvlist_t`, takes a rule reference, and links it into a caller-provided list.

`dacf_process_rsrvs()` walks a reservation list for a requested operation. Depending on flags, it invokes matching reservations with `dacf_op_invoke()` and/or releases them. `dacf_clr_rsrvs()` is a thin wrapper for releasing reservations for a device node and operation.

## Module Registration

`dacf_module_register()` registers a DACF module’s exported `struct dacfsw`. It validates the module revision, counts exported opsets, rejects empty non-kernel modules, and stores a copied opset table in `dacf_module_hash`.

The module object has a reader-writer lock:

- Registration and unregistration take writer access.
- Invocation takes reader access to keep the opset table stable while calling into a module operation.

`dacf_module_unregister()` marks a module unloaded and destroys copied opsets, unless module autounloading is blocked or the module lock cannot be acquired. The synthetic `__kernel` module is not allowed to unregister.

`dacf_destroy_opsets()` frees copied opset names and operation arrays. `dacf_opset_copy()` deep-copies the opset descriptor and terminates the copied operation list with `DACF_OPID_END`.

## Operation Invocation

`dacf_op_invoke()` is the core dispatcher. Given a rule and per-minor info handle, it:

- Finds or loads the target DACF module.
- Takes the module lock as reader.
- Locates the requested opset by name.
- Locates the operation matching the rule’s `r_opid`.
- Marks the devinfo node as invoking DACF to prevent recursive matching deadlocks.
- Drops `dacf_lock` before calling the operation function.
- Reacquires `dacf_lock`, clears the invoking marker, releases the module lock, and normalizes the return code.

It may call `modload("dacf", rule->r_module)` repeatedly until the module registers or loading fails. The `dacf_modload_laps` counter is diagnostic.

## Public DACF Helpers

The lower portion exposes helpers intended for DACF modules:

- Device/minor inspection: `dacf_minor_name`, `dacf_minor_number`, `dacf_get_dev`, `dacf_driver_name`, `dacf_devinfo_node`.
- Argument lookup: `dacf_get_arg`.
- Per-minor opaque data: `dacf_store_info`, `dacf_retrieve_info`.
- Vnode creation for a minor: `dacf_makevp`.

It also provides string-to-enum and enum-to-string helpers for device specifiers, operations, and options.

## Dependencies

The file depends on:

- `mod_hash` for rule, module, and info tables.
- Kernel module loading through `modload`.
- DDI minor data and devinfo internals.
- `dacf_impl.h` structures and flags.
- `kmod_dacfsw`, defined by `dacf_clnt.c`.

## Research Notes

Important invariants are that rule and module metadata are protected by `dacf_lock`, module opsets are protected by `dm_lock`, and DACF drops `dacf_lock` before invoking module callbacks. The main audit hotspots are recursive DACF invocation handling, module load/unload races, reservation reference counts, and opaque per-minor data lifetime because `dacf_info_hash` deliberately has no destructor.
