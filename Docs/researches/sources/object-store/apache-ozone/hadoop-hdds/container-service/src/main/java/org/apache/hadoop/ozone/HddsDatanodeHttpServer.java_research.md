# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/HddsDatanodeHttpServer.java

## Purpose
Datanode HTTP server wrapper providing standard monitoring endpoints such as `/conf`, `/prom`, and profiler endpoints.

## Important APIs, Types, And Functions
Extends `BaseHttpServer` with service name `hddsDatanode` and overrides config-key accessors for HTTP address, bind host, enabled flag, auth type, and auth config prefix.

## Control Flow
The datanode service constructs and starts it during startup, then reads bound HTTP/HTTPS addresses based on `HttpConfig.Policy` to publish ports in datanode details and JMX.

## State And Persistence
State is inherited from `BaseHttpServer`; this class itself adds no fields.

## Dependencies And Integration Points
Depends on `MutableConfigurationSource`, HDDS HTTP server framework, and `HddsConfigKeys`.

## Risks
Misconfigured bind/auth keys affect endpoint exposure. Startup failures are caught by `HddsDatanodeService`, which may continue without HTTP endpoints.

## Test Signals
Signals include HTTP/HTTPS bind, endpoint availability, auth behavior, published datanode ports, and clean shutdown.
