# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/EmptyContentTypeFilter.java

Purpose: `EmptyContentTypeFilter` normalizes requests whose `Content-Type` is the empty string, a compatibility path for clients such as older Ruby SDK behavior.

Important APIs and flow: as a servlet `Filter`, `doFilter` checks `HttpServletRequest.getContentType()`. If it equals `""`, the request is wrapped so `getContentType`, `getHeader("Content-Type")`, and `getHeaders("Content-Type")` return null, and `getHeaderNames()` skips `Content-Type` through `EnumerationWrapper`. Otherwise the original request passes through unchanged.

State, dependencies, risks, and tests: no persistent state exists. It integrates before Jersey routing and message body reader selection. Risks include `getHeaders("Content-Type")` returning null instead of an empty enumeration, and `EnumerationWrapper.step()` only skipping one adjacent content-type entry per step. Tests should cover empty content type removal, non-empty pass-through, enumeration behavior, and Jersey method routing for SDK requests.
