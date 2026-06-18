## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OzoneClientCreator.java

Purpose: Freon subcommand `occ`/`ozone-client-creator` that measures client creation and close overhead.

Important APIs/types/functions: option `--om-service-id`; `call` initializes Freon, stores config, creates `client-create` timer, and runs `createClient`; `createClientSafely` creates and immediately closes an Ozone RPC client.

Control flow: each task times a client create/close cycle. Exceptions are wrapped in `RuntimeException` so BaseFreonGenerator counts failures.

State and persistence behavior: no Ozone metadata persistence; local state is config and timer.

Dependencies and integration points: `BaseFreonGenerator.createOzoneClient`, Ozone client factory.

Risks: high counts can create connection churn against OM; wrapped exceptions lose checked exception type; no extra validation of OM service ID.

Test signals: timer count should match success count; resource leaks show as open connections/threads after run.
