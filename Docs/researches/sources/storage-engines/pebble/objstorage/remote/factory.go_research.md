# sources/storage-engines/pebble/objstorage/remote/factory.go

Purpose: This file provides a simple map-backed implementation of `remote.StorageFactory` for tests and small integrations.

Important APIs and types: `MakeSimpleFactory` converts a `map[Locator]Storage` into a `StorageFactory`. The private `simpleFactory` type implements `CreateStorage(locator Locator)`.

Control flow and state: `CreateStorage` performs a direct map lookup. If the locator exists, it returns the preconfigured storage instance. If not, it returns an error containing the redacted locator string. There is no cloning or lifecycle ownership beyond returning the stored object reference.

Dependencies and integration: Provider settings use `Remote.StorageFactory` to resolve locators found in the remote object catalog or encoded backings. Tests frequently use `MakeSimpleFactory` with `remote.NewInMem` stores for deterministic remote behavior.

Risks and test signals: Because returned storage instances are shared, tests can model multiple providers pointing at the same remote storage. Unknown locators fail at attach/open/init time, which provider tests exercise in the multi-locator attach case. Production storage factories would typically perform credential/config lookup instead of a static map.
