# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/event/SMBEventBus.java

Purpose: `SMBEventBus` wraps MBassador so the rest of SMBJ depends on a local event facade.

Important APIs and control flow: default construction uses a synchronous MBassador bus with an error handler that logs publication errors. `subscribe`, `unsubscribe`, and `publish` delegate to the wrapped bus.

State, dependencies, and integration: used by `SMBClient`, `Connection`, sessions, and tree connections for lifecycle cleanup.

Risks: synchronous publication means handler exceptions are logged by MBassador but can affect timing. Tests should cover subscription, unsubscription, publication, and error logging with a fake or real bus.
