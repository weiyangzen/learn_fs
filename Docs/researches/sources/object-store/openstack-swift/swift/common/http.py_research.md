# sources/object-store/openstack-swift/swift/common/http.py

Purpose: provides common HTTP status classifiers and named status-code constants used across Swift without repeatedly importing larger HTTP frameworks.

Important APIs/types/functions: `is_informational`, `is_success`, `is_redirection`, `is_client_error`, and `is_server_error` check status-code ranges. Constants cover common 1xx through 5xx codes plus Swift/vendor-specific values such as 498, 499, 529 consumers via other modules, and network timeout pseudo-codes 598/599.

Control flow: classifier functions are direct numeric range checks. The rest of the file is constant definitions grouped by status class.

State and persistence: no mutable or persistent state.

Dependencies and integration: self-contained. Imported by clients, middleware, proxy, object, container, account, and tests for readable status comparisons.

Risks: constants are manually maintained, including misspellings kept for compatibility such as `HTTP_UPGRADE_REQUIED`; classifiers assume integer status inputs; non-standard codes are intentionally included and may not match external libraries. Tests should verify range helpers and any code paths depending on non-standard constants.
