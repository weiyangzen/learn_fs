<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/dbus/properties_handler.c -->
## sources/user-network-fs/nfs-ganesha/src/dbus/properties_handler.c

Purpose: implementation of the standard `org.freedesktop.DBus.Properties` methods for Ganesha D-Bus objects.

Important APIs/functions: `lookup_interface()` resolves a named interface, with a fake properties interface for scanners. `lookup_property()` finds a property descriptor by name. `dbus_proc_property()` handles `GetAll`, `Get`, and `Set`, appending variants and dictionaries through `DBusMessageIter` and invoking per-property get/set callbacks from `struct gsh_dbus_prop`.

Control flow/state: no persistent state beyond static `props_interface`. `GetAll` iterates readable/readwrite properties and builds `a{sv}`. `Get` opens one variant and calls the property getter. `Set` validates exact argument shape of interface, property name, and variant, then recurses into the variant for the property setter.

Dependencies/integration: depends on D-Bus error names, Ganesha interface/property descriptor structures, and callback functions supplied by each registered object interface. Used by `dbus_message_entrypoint()` when method calls target `DBUS_INTERFACE_PROPERTIES`.

Risks: `Get` calls `(*prop)->get(&variant_iter)` twice before closing the variant, which can duplicate appended data or trigger getter side effects. `GetAll` treats write-only properties as a read-only error rather than omitting them, which may surprise standard clients. Setter failures return false without always setting a detailed D-Bus error.

Test signals: D-Bus clients should exercise `Get`, `GetAll`, `Set`, unknown interface/property, read-only write, and malformed argument paths, including a getter that can detect double invocation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/dbus/properties_handler.c -->
