# sources/test-tools/syzkaller/dashboard/app/handler.go

Purpose: common HTTP middleware and UI helpers for context, auth, throttling, template rendering, page headers, namespace cookies, redirects/errors, and gzip buffering.

Important APIs/types/functions: `contextHandler`, `handlerWrapper`, `handleContext`, `logErrorPrepareStatus`, `isRobot`, `backpressureRobots`, `throttleRequest`, `ErrClient`, `ErrRedirect`, `handleAuth`, `serveTemplate`, `uiHeader`, `commonHeaderRaw`, `commonHeader`, `decodeCookie`, `encodeCookie`, `gzipResponseWriterCloser`, and `newGzipResponseWriterCloser`.

Control flow: `handleContext` stores current URL, throttles unauthenticated users, buffers handler output through gzip, flushes only on success, and maps access/client/redirect/internal errors to redirects or error templates. `commonHeader` resolves namespace from route/cookie/defaults, filters accessible namespaces, redirects invalid paths, stores namespace cookie, and loads cached bug stats.

State/persistence: writes a long-lived base64 JSON `syzkaller` cookie; otherwise delegates persistence to throttling/cache layers.

Dependencies/integration: depends on App Engine user/log APIs, access/config/cache helpers, `pkg/html`, gzip/JSON/base64, and all UI handlers using `contextHandler`.

Risks/test signals: buffered responses can interact subtly with early `WriteHeader`; malformed cookies are silently ignored; plain oversized responses fail only after generation. `handler_test.go` covers gzip/plain output, headers, and status preservation.
