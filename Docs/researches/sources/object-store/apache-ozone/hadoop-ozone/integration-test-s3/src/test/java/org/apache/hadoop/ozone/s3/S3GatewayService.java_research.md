# sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/S3GatewayService.java

## Purpose

This mini-cluster service starts a single Ozone S3 Gateway for integration tests and binds its HTTP, HTTPS, and webadmin endpoints to free localhost ports.

## Important APIs, types, and functions

The class implements `MiniOzoneCluster.Service` and defines `start()`, `stop()`, `toString()`, `getConf()`, and private `configureS3G()`. It owns a `Gateway` instance and uses `OzoneConfigurationHolder` to pass the configured S3G addresses to the gateway.

## Control flow, state, and persistence

`start()` asserts no gateway is running, clones the input configuration, sets all S3G and webadmin bind addresses to free localhost ports, resets and sets `OzoneConfigurationHolder`, creates `Gateway`, and executes it with no args. `stop()` asserts a gateway exists and stops it. Runtime state is the running gateway and global configuration holder; no test data is persisted by this wrapper.

## Dependencies and integration points

It integrates `Gateway`, `S3GatewayConfigKeys`, `OzoneConfigurationHolder`, `MiniOzoneCluster.Service`, and port allocation utilities. `MultiS3GatewayService` composes several instances and reads each child's `getConf()` to discover its HTTP endpoint.

## Risks and test signals

Because it uses a global `OzoneConfigurationHolder`, multiple gateway instances rely on each service starting and capturing its configuration correctly. `stop()` does not null out `s3g`, so a stopped instance cannot be restarted by the same object without failing the start assertion. Positive signals are unique free ports, a `toString()` showing live HTTP/HTTPS addresses, and SDK clients successfully reaching the configured S3G endpoint.
