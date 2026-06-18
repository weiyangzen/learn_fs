# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/Request.java

Purpose: `Request` represents one outstanding SMB request and its response promise.

Important APIs and control flow: constructor stores original packet, message ID, cancel ID, timestamp, and creates a `Promise`. Async handlers may set `asyncId`. `getFuture` wraps the promise future in a cancellable future with a callback.

State, dependencies, and integration: used by `OutstandingRequests`, `Connection.send`, async response handling, cancellation, and response processing.

Risks: original packet reference is mutable; converter depends on it to deserialize matching responses. Tests should cover promise delivery, cancellation callback invocation, async ID update, and timestamp availability for logging.
