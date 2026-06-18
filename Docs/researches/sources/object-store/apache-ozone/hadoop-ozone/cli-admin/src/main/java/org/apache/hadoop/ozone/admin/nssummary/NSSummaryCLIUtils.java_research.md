# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/nssummary/NSSummaryCLIUtils.java

## Purpose
Provides shared utilities for namespace summary CLI commands, including Recon HTTP calls, path parsing, and text formatting helpers.

## Important APIs, Types, And Functions
`makeHttpCall` overloads append query parameters, open a `URLConnectionFactory` connection with optional SPNEGO, handle HTTP OK/CREATED, and return response text. Formatting helpers print spaces, newlines, empty/path-not-found/type-not-applicable messages, key-value separators, and underlined headings. `parseInputPath` strips `ofs://authority` to the path component.

## Control Flow
HTTP calls append `?path=...`, optional `files=true` and `replica=true`, print the target URL, connect, read the input stream for successful status, print initialization or unexpected payload messages for other statuses, and handle connection refused/authentication exceptions by returning null.

## State And Persistence
Stateless. It performs network reads from Recon and writes user-facing output.

## Dependencies And Integration Points
Depends on HDFS `URLConnectionFactory`, Ozone configuration, Java `HttpURLConnection`, Apache Commons IO, picocli ANSI, and Recon REST APIs.

## Risks And Test Signals
The path and query parameters are not URL-encoded, and `getInputStream()` is called before checking non-success error streams, which may throw for HTTP errors. Tests should cover URL encoding-sensitive paths, SPNEGO flag, HTTP error responses, connection refused, auth failure, OFS path parsing, and formatting helpers.
