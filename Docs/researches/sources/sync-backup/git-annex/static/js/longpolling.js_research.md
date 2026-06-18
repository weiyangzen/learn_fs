# sources/sync-backup/git-annex/static/js/longpolling.js

Purpose: small git-annex web UI polling helper that repeatedly fetches HTML or text endpoints and lets callers continue, refresh UI fragments, or fail after repeated connection failures.

Important APIs/types/functions: global `connfails`, global `longpollcallbacks = $.Callbacks()`, `longpoll_div(url, divid, cont, fail)`, and `longpoll_data(url, cont)`.

Control flow: `longpoll_div` issues an HTML AJAX request, replaces the DOM element with matching `divid` on success, fires registered callbacks, resets failure count, and invokes `cont()`. On error it increments `connfails`; above 12 failures it calls `fail()`, otherwise it calls `cont()` to keep polling. `longpoll_data` issues a text AJAX request and calls `cont(1, data)` on success or `cont(0)` on failure.

State/persistence behavior: only global in-memory failure count and callback list are maintained. DOM replacement is the primary observable state change. There is no durable persistence, retry backoff, or cancellation token in this file.

Dependencies/integration: depends on jQuery AJAX and callback APIs. Callers provide continuation functions, so scheduling/repetition lives outside the helper. `longpollcallbacks` allows other UI modules to rerun behaviors after a div replacement.

Risks/test signals: `connfails` is shared across all long-poll elements, so one failing endpoint can affect another. The 12-failure threshold assumes up to four elements and expected failures during navigation. Tests should simulate success, repeated failure, DOM replacement, callback firing, and independent callers sharing the global failure counter.
