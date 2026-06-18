# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_prop.c

## Role

Implements ZFS DSL property lookup, inheritance, received-property handling, property callbacks, and sync-task based property setting.

## Property Sources

The file models property source state with ZAP names:

- Local property: `<propname>`
- Explicit inherit marker: `<propname>$inherit`
- Received property: `<propname>$recvd`

`dodefault()` provides built-in defaults for valid properties, including set-once read-only defaults.

## Property Lookup

- `dsl_prop_get_dd()` walks a `dsl_dir_t` and its parents, respecting inheritable status, local values, explicit inheritance markers, received values, snapshot lookup behavior, and defaults.
- `dsl_prop_get_ds()` first checks snapshot-specific `ds_props_obj` when present, then falls back to directory lookup.
- Convenience wrappers include `dsl_prop_get()`, `dsl_prop_get_integer()`, and `dsl_prop_get_int_ds()`.

## Prediction and Quota/Reservation Handling

`dsl_prop_predict()` computes the effective value for quota/reservation/refquota/refreservation under a proposed source/value mutation. It handles old pools without received-property support by mapping received source to local behavior.

## Callback Infrastructure

Each `dsl_dir_t` owns property records, each record owns callback records:

- `dsl_prop_init()` / `dsl_prop_fini()` manage the directory property list.
- `dsl_prop_register()` registers callbacks and immediately invokes them with the current integer value.
- `dsl_prop_unregister_all()` removes callbacks by callback argument.
- `dsl_prop_notify_all()` recursively refreshes descendants, mainly after rename.
- `dsl_prop_changed_notify()` recursively propagates inherited integer property changes until overridden locally.

Important lifetime handling: callback records do not hold datasets, so notification paths use `dsl_dataset_try_add_ref()` for snapshot callback datasets that may be under eviction.

## Property Setting

- `dsl_prop_set_sync_impl()` applies source-specific mutations to local, inherit, and received ZAP entries, creates snapshot property ZAPs when needed, emits callbacks for integer properties, and logs history.
- `dsl_props_set_check()` validates dataset existence, property name length, string value length, and snapshot property support.
- `dsl_props_set()` wraps property updates in `dsl_sync_task()` and estimates modified blocks unless only clearing entries.

The setting path is intended to be all-or-nothing: check happens before sync mutation.

## Enumerating Properties

- `dsl_prop_get_all_impl()` converts ZAP entries to nested nvlists with `ZPROP_VALUE` and `ZPROP_SOURCE`, filtering local/received/inherited/snapshot validity.
- `dsl_prop_get_all_ds()` walks snapshot props and parent dirs as needed.
- `dsl_prop_get_all()` returns effective properties for an objset.
- `dsl_prop_get_received()` returns received properties when distinguishable, otherwise local properties for compatibility.
- `dsl_prop_nvlist_add_uint64()` and `dsl_prop_nvlist_add_string()` add or update formatted property entries.

## Compatibility Notes

Pools older than `SPA_VERSION_RECVD_PROPS` collapse received-source semantics into local-source behavior. Snapshot properties require `SPA_VERSION_SNAP_PROPS`.
