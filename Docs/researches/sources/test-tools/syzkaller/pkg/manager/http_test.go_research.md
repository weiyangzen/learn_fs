# sources/test-tools/syzkaller/pkg/manager/http_test.go

Purpose: Provides focused tests for HTTP template validity and same-site redirect protection.

Important tests: `TestHttpTemplates` iterates over `templTypes`, fills each template data type with randomized values from `testutil.RandValue`, and executes the template into `io.Discard`. `TestLocalRedirectURL` validates accepted local paths and rejection of absolute URLs, protocol-relative URLs, slash/backslash variants, and `javascript:` strings.

Control flow and state: Template registration happens at package init through `createPage`, which appends each template/data pair into `templTypes`. The redirect test calls the pure helper `localRedirectURL`.

Dependencies and integration: Ties the embedded manager HTML templates to their Go UI structs. The redirect test protects `httpAction`, which redirects after expert/pause actions.

Risks: Random data checks template execution but not semantic rendering, browser behavior, route coverage, or handler status codes. Redirect validation currently allows only one path segment with word/dot/hyphen characters and optional query; expanding allowed URLs needs test updates.

Test signals: Good guard against template field drift and open-redirect regressions in the action endpoint.
