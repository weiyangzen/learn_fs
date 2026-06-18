# File Research: sources/os/linux/linux/fs/efivarfs/vars.c

Implements EFI variable validation, name conversion, enumeration, and firmware get/set/delete wrappers.

Key behavior:
- Validates known sensitive EFI variables such as BootOrder, Boot####, Driver####, console paths, language strings, timeout, and OS indications.
- Load-option validation checks hex suffixes, descriptor length, file-path length, and valid EFI device-path termination.
- Maintains a sorted validation/whitelist table; variables in the table are considered removable.
- `efivar_get_utf8name()` converts UTF-16 variable names to `name-guid` UTF-8 filenames and replaces slashes with `!`.
- `efivar_validate()` converts names to UTF-8 and dispatches matching validators.
- `efivar_init()` iterates firmware variables under `efivar_lock()`, handles old firmware buffer-size quirks, detects duplicate variables when requested, and calls a supplied callback for each variable.
- `efivar_entry_delete()` deletes a variable by calling SetVariable with zero attributes and size.
- `efivar_entry_size()` gets variable size through the expected `EFI_BUFFER_TOO_SMALL` status.
- `efivar_entry_get()` wraps GetVariable with locking.
- `efivar_entry_set_get_size()` validates data, sets the variable, then re-queries size to detect overwrite, append, or deletion.

Important interactions:
- Imports the `EFIVAR` namespace.
- Provides the policy boundary that prevents malformed boot variables from being written through efivarfs.
- Locking centralizes EFI runtime service access and keeps set/get-size behavior atomic.
