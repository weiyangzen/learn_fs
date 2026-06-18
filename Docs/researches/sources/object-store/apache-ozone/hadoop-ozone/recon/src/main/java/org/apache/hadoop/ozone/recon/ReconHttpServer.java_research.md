# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconHttpServer.java

## Purpose
`ReconHttpServer` specializes `BaseHttpServer` with Recon-specific configuration keys, defaults, authentication settings, and bind ports.

## Important APIs, Types, And Functions
The constructor calls `super(conf, "recon")`. Overridden methods return HTTP/HTTPS address keys, bind-host keys/defaults, port defaults, Kerberos keytab/principal keys, enabled key, auth type, and auth config prefix.

## Control Flow
`ReconServer` obtains this singleton from Guice and calls `start()` and `stop()` through the base class. All address/security behavior is delegated to `BaseHttpServer` using the provided keys.

## State And Persistence
Server runtime state is held in the superclass. No Recon-specific persistence exists here.

## Dependencies And Integration Points
It depends on `OzoneConfiguration`, `BaseHttpServer`, `ReconConfigKeys`, and `ReconServerConfigKeys`. It serves the Jersey/Guice servlet bindings configured by `ReconRestServletModule`.

## Risks
Misconfigured key names or defaults break endpoint reachability. HTTP auth and SPNEGO depend on the keytab/principal values returned here matching the deprecation mappings and docs.

## Test Signals
Tests should verify address/default resolution, enabled/disabled behavior, HTTP security integration, and server lifecycle under Recon configuration.
