# sources/object-store/garage/src/garage/tests/s3/website.rs

Purpose: This large integration file tests Garage's S3 website hosting and related Admin API domain check behavior. Coverage includes CLI and S3-API website enablement, index/error documents, CORS, redirect metadata, routing rules, punycode domains, invalid redirects, and default not-found pages.

Important APIs and types: Tests include `test_website`, `test_website_s3_api`, `test_website_check_domain`, `test_website_redirect_full_bucket`, `test_website_redirect`, `test_redirect_helper`, `test_website_invalid_redirect`, `test_website_puny`, and `test_website_object_not_found`. They use AWS SDK website/CORS types, Hyper direct requests to the web/admin ports, `LOCATION`, JSON body assertions, and CLI `bucket website --allow/--deny`.

Control flow: The CLI website test verifies web access denied before enablement, admin `/check` failure, enablement via CLI, successful serving and domain checks for plain/web/s3 host forms, then disablement and failure again. The S3 API test stores index/error objects, configures website and CORS through S3 APIs, validates direct web GET, error document, object redirect metadata, allowed/forbidden preflights, CORS deletion, and website deletion. Redirect tests validate full-bucket and rule-based redirects/rewrites, including conditional rules that only apply on 404. Additional tests check missing `domain`, invalid domains, invalid redirect config, punycode host serving, and default HTML 404 content.

State and persistence behavior: The file persists objects, website configurations, CORS configurations, bucket website exposure state, routing rules, redirect metadata, and admin domain-management state. It validates that disabling/deleting configs changes web serving immediately in the single-node instance.

Dependencies and integration points: It exercises the S3 Web server, S3 bucket website API, bucket metadata, admin API `/check`, CORS evaluation, object metadata redirects, routing rule evaluator, bucket alias/domain matching, and CLI admin commands.

Risks: Tests use direct Hyper requests with explicit Host headers and fixed bucket names, so they rely on test instance isolation. Some edge cases are commented out, such as empty domain handling. The redirect helper has repeated `stream-404` assertions and does not separately inspect the `stream-missing` path despite configuring it.

Test signals: HTTP statuses 200/302/307/301/403/404/400, exact `Location` headers, exact served bodies for index/error/static files, JSON admin error bodies, CORS headers and deletion errors, round-tripped website config, invalid config rejection, punycode host success, and default not-found content type/body.
