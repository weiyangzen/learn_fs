<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestHtmlQuoting.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestHtmlQuoting.java

Purpose: tests HTML escaping/unescaping helpers and the servlet request wrapper used to quote request parameters.

Important APIs/types/functions: `HtmlQuoting.needsQuoting`, `quoteHtmlChars`, `unquoteHtmlChars`, `HttpServer2.QuotingInputFilter.RequestQuoter`, `HttpServletRequest.getParameter`, and `getParameterValues`.

Control flow: unit tests check which strings require quoting, expected replacements for `<`, `>`, `&`, quotes, and apostrophes, and round-trip quote/unquote for representative inputs. Request-quoting tests mock a servlet request, return single and array parameter values, and assert the wrapper quotes values while preserving nulls.

State and persistence behavior: no external state. All transformations are pure string operations over in-memory servlet mocks.

Dependencies and integration points: integrates HTML quoting utilities with `HttpServer2` input-filter request wrapping and servlet APIs.

Risks: escaping coverage is security-relevant for XSS prevention. The tests cover common characters but not every Unicode or malformed entity edge case.

Test signals: asserts quoting-needed decisions, exact escaped strings, null passthrough, round-trip behavior, quoted single request parameter, quoted parameter array, and null parameter-array passthrough.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestHtmlQuoting.java -->
