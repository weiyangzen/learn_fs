# sources/sync-backup/kopia/internal/clock/now_testing.go

Purpose: testing-build implementation of `clock.Now` that can be overridden by a fake time HTTP endpoint.

Important APIs/types/functions: build tag `testing`, variable `Now`, `init`, `getTimeFromServer`, and constant `refreshServerTimeEvery`.

Control flow: default `Now` mirrors production. During init, `KOPIA_FAKE_CLOCK_ENDPOINT` replaces `Now` with a closure that fetches `{time, validFor}` JSON over HTTP, caches an offset from real local time to server time, and refreshes after `validFor` expires.

State and persistence behavior: closure state includes a mutex, latest server time info, next refresh real time, and local offset. No persistent writes. Fatal logging aborts tests on endpoint failures or malformed responses.

Dependencies/integration: uses `net/http`, `encoding/json`, `os`, `sync`, and `log`. Supports integration/fake-time tests across processes.

Risks/test signals: uses `http.Get` without context and `log.Fatalf`, so fake endpoint issues terminate the process. No direct tests are listed; coverage is mostly through testing builds that set the environment variable.
