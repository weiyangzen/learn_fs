# sources/user-network-fs/gcsfuse/tools/proxy_server/emulator.go

Purpose: client helper for creating retry-test resources in a storage emulator/proxy target.

Important APIs/types/functions: `emulatorTest`, `RetryTestClient`, `(*emulatorTest).GetRetryID`, and `CreateRetryTest`.

Control flow: encodes retry instructions and transport to JSON, posts to `<host>/retry_test`, requires HTTP 200, decodes returned `id`, and returns it. Empty instruction maps return an empty id without a request.

State/persistence behavior: mutates the `host.Path` field during the request and resets it afterward. Remote emulator state is created by the POST.

Dependencies/integration: called by `AddRetryID` to plant emulator behavior and add `x-retry-test-id` to proxied requests.

Risks/test signals: response body close errors are ineffectively assigned to the local `err` in a defer after return values are fixed. Mutating a shared `url.URL` would not be safe across concurrent calls.
