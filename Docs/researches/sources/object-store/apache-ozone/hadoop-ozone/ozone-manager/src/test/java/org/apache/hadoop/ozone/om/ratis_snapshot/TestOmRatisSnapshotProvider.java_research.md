# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ratis_snapshot/TestOmRatisSnapshotProvider.java

Purpose: tests multipart form-data generation and download request setup in `OmRatisSnapshotProvider`.

Important APIs/types: `OmRatisSnapshotProvider`, `URLConnectionFactory`, `OMNodeDetails`, `HttpURLConnection`, `HttpConfig.Policy`, `OzoneConsts.MULTIPART_FORM_DATA_BOUNDARY`, and `OZONE_DB_CHECKPOINT_REQUEST_TO_EXCLUDE_SST`.

Control flow: setup builds a provider with temporary snapshot/download directories, a mocked leader node map, mocked HTTP policy, and mocked connection factory. `testDownloadSnapshot` makes the leader return a checkpoint URL, mocks connection output/input streams and HTTP 200 status, invokes `downloadSnapshot`, and verifies the request body contains an empty exclude-SST multipart field and closing boundary. Other tests call static `writeFormData` with one SST filename or an empty list and compare the exact wire body.

State and persistence behavior: target file is prepared in a temporary download directory, but assertions focus on request body bytes rather than downloaded content. No durable state remains.

Dependencies and integration points: integrates snapshot provider HTTP download path with leader endpoint generation and checkpoint exclude-list protocol. Uses Java `HttpURLConnection` and HDFS `URLConnectionFactory`.

Risks: exact CRLF and boundary matching is intentionally strict. The download test uses an empty input stream derived before body writes, so it mainly tests outgoing form data, not actual file copy behavior.

Test signals: validates multipart field name, boundary format, optional SST filename inclusion, closing delimiter, and provider use of leader checkpoint endpoint/connection factory.
