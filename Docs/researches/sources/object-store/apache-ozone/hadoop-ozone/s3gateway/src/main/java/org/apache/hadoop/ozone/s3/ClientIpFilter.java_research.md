# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/ClientIpFilter.java

Purpose: `ClientIpFilter` records the client IP address into request headers for later audit and request-context use.

Important APIs and flow: it is a pre-matching request filter with priority after header preprocessing. It reads `x-real-ip`; if absent, it uses the first `x-forwarded-for` address; if still absent, it uses `HttpServletRequest.getRemoteAddr()`. The selected value is written as `client_ip`.

State, dependencies, risks, and tests: no persistent state is held; the only state mutation is adding a request header. It depends on servlet request injection and Jersey request filtering. Risks include trusting unvalidated forwarded headers and not trimming whitespace from multi-hop `x-forwarded-for`. Tests should cover header precedence, forwarded header parsing, and remote-address fallback; audit tests indirectly depend on this header.
