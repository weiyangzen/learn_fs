# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/Gateway.java

Purpose: `Gateway` is the picocli/HDDS CLI entry point for the Ozone S3-compatible REST service.

Important APIs and flow: `main` disables JVM network address caching if configured and runs the command. `call()` loads the `OzoneConfiguration`, stores it in `OzoneConfigurationHolder`, initializes tracing and UGI, performs Kerberos login when security is enabled, sets HTTP base dir, constructs the S3 API server and web-admin/content server, creates S3G and Netty metrics, starts services, and registers a shutdown hook. `start()` emits startup metadata, initializes metrics, starts the JVM pause monitor and both servers. `stop()` closes servers, stops pause monitoring, and unregisters metrics.

State, dependencies, risks, and tests: runtime state is server handles, metrics handles, and a pause monitor. Persistence is limited to logs/metrics and served static files. It depends on HDDS server framework, security utilities, tracing, Ozone configuration, and shutdown hooks. Risks include unsupported non-Kerberos security methods, partial startup cleanup, static configuration reuse in tests, and content-server failures affecting the S3 API process. Tests generally verify address accessors, startup under mini-cluster configs, and security login behavior.
