# sources/user-network-fs/samba/source4/torture/ndr/winspool.c

Purpose: This file is a narrow NDR regression suite for the generated `winspool` parser. It validates that a captured NDR64 `SyncRegisterForRemoteNotifications` input buffer decodes into the expected remote notification filter structure.

Important APIs, types, and functions: The fixture is `registerforremotenotifications_req_data`. `registerforremotenotifications_req_check()` inspects `struct winspool_SyncRegisterForRemoteNotifications`, `struct winspool_PrintNamedProperty`, and nested `struct spoolss_NotifyOption` values. `ndr_winspool_suite()` registers the test with `torture_suite_add_ndr_pull_fn_test_flags()` using `NDR_IN` and `LIBNDR_FLAG_NDR64`.

Control flow: The suite creates a `winspool` torture suite, feeds the static byte array into the generated pull function, then calls the checker. The checker asserts the notification filter exists, contains four named properties, and that the fourth property carries a two-entry `spoolss_NotifyOption`: one printer notify type with ten printer fields and one job notify type with sixteen job fields.

State and persistence behavior: There is no live server state and no persistence. The only state is the immutable capture vector and decoded transient talloc-backed NDR result.

Dependencies and integration points: The file integrates with Samba's NDR torture harness, generated `librpc/gen_ndr/ndr_winspool.h`, spoolss notify constants, and `torture/ndr/proto.h`. It is exposed through `ndr_winspool_suite()` for the broader NDR torture runner.

Risks: The fixture is intentionally brittle against IDL layout changes, NDR64 alignment changes, property union changes, and notify field enum renumbering. It only exercises one request shape and does not cover output unmarshalling or malformed input.

Test signals: A passing test proves the generated winspool NDR64 pull path maps named properties, property unions, string values, and nested spoolss notify options exactly as expected for this captured request. Failures point to NDR conformance, IDL, or enum mapping regressions.
