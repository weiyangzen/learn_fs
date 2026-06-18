# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/VirtualHostStyleFilter.java

Purpose: `VirtualHostStyleFilter` converts configured S3 virtual-host-style requests into path-style URIs before resource matching.

Important APIs and flow: on each request it reads `ozone.s3g.domain.name`. If no domains are configured, it returns. It strips a port from the `Host` header, picks the longest configured suffix matching the host, and throws `InvalidRequestException` if none matches. If the host has a bucket prefix before the domain, it validates the prefix ends with `.`, removes the dot, rebuilds the request URI as `/{bucket}/{currentPath}`, and preserves query parameters.

State, dependencies, risks, and tests: state is the injected configuration and a per-request domains array. It integrates after signature processing and before header preprocessing/resource matching. Risks include simplistic port stripping for IPv6 host literals, host-header trust, longest-suffix domain ambiguity, and invalid request exceptions not using S3 XML errors unless mapped. Tests should cover path style, virtual-host rewrite, multiple domains, query preservation, bad hosts, and ports.
