## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/quota/QuotaRepair.java

Purpose: `om quota` command group and shared OM-client factory for quota repair status/start commands.

Important APIs and control flow: registers `QuotaStatus` and `QuotaTrigger`. `createOmClient` chooses connection mode from `--service-host`, `--service-id`, or the only configured service ID. It installs the protobuf RPC engine, creates an OM transport through `Hadoop3OmTransportFactory`, and returns an `OzoneManagerProtocolClientSideTranslatorPB`. If `forceHA` is true it verifies the supplied ID is an HA service ID. Helpers expose configured OM service IDs and current user.

State and dependencies: no direct persistence; returned clients invoke live OM RPCs. Dependencies include OM config keys, Hadoop RPC, OM transport factory, UGI, and Ratis `ClientId`.

Risks and test signals: ambiguous or missing service ID in multi-OM configurations fails early. Direct host mode bypasses HA routing and must target the leader for some operations. No direct quota tests in this subset.
