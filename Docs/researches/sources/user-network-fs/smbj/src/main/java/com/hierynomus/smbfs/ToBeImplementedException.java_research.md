# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/ToBeImplementedException.java

Purpose: `ToBeImplementedException` is a package-local helper for explicit unsupported SMB filesystem SPI methods.

Important APIs and control flow: the private constructor prevents arbitrary message variants; static `toBeImplemented()` returns a new `UnsupportedOperationException` subclass.

State, dependencies, and integration: it has no state. It is statically imported throughout `smbfs` to mark unsupported NIO operations such as file stores, watch services, attribute views, path matching, and unsupported options.

Risks: the exception has no message, so failures can be opaque. Tests should assert unsupported paths throw this subtype or `UnsupportedOperationException` as expected, while supported NIO flows never route here unexpectedly.
