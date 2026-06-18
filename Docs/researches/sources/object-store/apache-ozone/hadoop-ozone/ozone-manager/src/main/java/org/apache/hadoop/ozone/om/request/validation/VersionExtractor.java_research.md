# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/validation/VersionExtractor.java

Purpose: `VersionExtractor` is an enum strategy for extracting a `Versioned` value from an `OMRequest` and validation context. It lets the validation framework use the same flow for metadata layout version validators and client protocol version validators.

Important APIs and types: `LAYOUT_VERSION_EXTRACTOR` returns the current `LayoutVersionManager` feature for the metadata layout version. `CLIENT_VERSION_EXTRACTOR` maps the request protobuf version to `ClientVersion`, using `FUTURE_VERSION` when the request advertises a newer version than the server. Each strategy exposes the validator annotation class through `getValidatorClass()`.

Control flow: The caller chooses an enum constant based on validator category, calls `extractVersion(req, ctx)`, then can compare that value against validator constraints. The client path is defensive against newer clients; the layout path reads from `ValidationContext.versionManager()`.

State and persistence behavior: The enum keeps no mutable state and persists nothing. It reflects runtime layout-manager state and request protobuf fields.

Dependencies and integration points: It bridges `OMLayoutVersionValidator`, `OMClientVersionValidator`, `ClientVersion`, `Versioned`, `OMRequest`, and `LayoutVersionManager`.

Risks and test signals: Tests should verify current layout feature extraction, exact protobuf-to-client-version mapping, and future-client fallback. A risk is that missing or stale version-manager state would make layout validation reject or allow requests incorrectly.
