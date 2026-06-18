## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/DNRPCLoadGenerator.java

Purpose: Freon subcommand `dn-echo`/`dne` for generating datanode echo RPC load against the datanodes associated with a container.

Important APIs/types/functions: extends `BaseFreonGenerator`, implements `Callable<Void>`. Options cover request/response payload KB, container ID, datanode sleep time, number of Xceiver clients, read-only flag, and Ratis vs gRPC mode. Main task is `sendRPCReq`.

Control flow: `call` validates payload sizes, gets config, fetches container info and matching pipeline from SCM, switches non-Ratis mode to read-only and `copyForRead`, gets a container token, creates secure or insecure `XceiverClientCreator`, acquires `numClients`, initializes Freon, generates protobuf payload, computes response size, runs tests, then closes OM, Xceiver clients, factory, and SCM client.

State and persistence behavior: no Ozone metadata mutation unless Ratis/write mode is requested by the underlying echo call. Local state stores clients, payload bytes, timer, and token.

Dependencies and integration points: uses SCM `ContainerOperationClient`, `ContainerProtocolCalls.echo`, Xceiver clients, Ozone security, OM service info for CA certificates, and payload utilities.

Risks: container ID must exist; response payload calculation clamps to `MAX_SIZE_KB` bytes despite name in KB; non-Ratis mode mutates `readOnly`; client release occurs after direct close paths need careful handling.

Test signals: validate payload validation, secure/insecure client setup, client index distribution, and echo RPC success against a test container.
