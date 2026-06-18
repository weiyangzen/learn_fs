## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OmRPCLoadGenerator.java

Purpose: Freon subcommand `om-echo`/`ome` that generates OM echo RPC load with configurable request/response payloads.

Important APIs/types/functions: options include request payload KB, response payload KB, number of clients, and `--ratis` to write to Ratis log. `call` creates OM protocol clients, generates payload, and runs `sendRPCReq`.

Control flow: validate nonnegative payload sizes, create `clientsCount` OM clients, initialize Freon, generate byte payload, set response size, create timer, run tasks, and close all clients.

State and persistence behavior: read-only echo by default; with `--ratis`, echo requests write through Ratis as implemented by OM. Local state is client array, payload, response size, and timer.

Dependencies and integration points: `BaseFreonGenerator.createOmClient`, Ozone OM protocol translator, payload utilities, metrics.

Risks: no upper bound enforcement despite help text mentioning max; payload size multiplication can overflow for very large integers; client count less than one is not normalized here.

Test signals: RPC success, payload handling, timer counts, and cleanup of clients.
