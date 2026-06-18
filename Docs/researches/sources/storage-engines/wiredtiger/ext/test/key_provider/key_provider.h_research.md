# sources/storage-engines/wiredtiger/ext/test/key_provider/key_provider.h

This header declares the test key provider's state machine and implementation structure. `KEY_STATE` defines current, pending, and read states. `KEY_PROVIDER` embeds `WT_KEY_PROVIDER` first for interface casting, stores `WT_EXTENSION_API`, config values (`version`, `verbose`, `key_expires`), and simulated key state (`lsn`, `timestamp`, `key_state`, `key_time`, `key_size`, `key_data`). It also declares `key_provider_extension_init`.

The comments document the valid pull-mode transitions and note that push mode bypasses the state machine. The header has no persistence itself; persisted state flows through `WT_CRYPT_KEYS`. Risks are mainly ABI/layout related: moving `iface` away from the first field would break casts, and the documented transition rules must stay aligned with `key_provider.c`. Compile tests in module and builtin modes are the main signal.
