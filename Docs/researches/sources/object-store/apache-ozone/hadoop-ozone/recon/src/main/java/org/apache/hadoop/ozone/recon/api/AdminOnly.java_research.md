# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/AdminOnly.java

## Purpose
`AdminOnly` marks JAX-RS resource classes whose endpoints should be restricted to Ozone or Recon administrators when HTTP authorization is enabled.

## Important APIs, Types, And Functions
It is a runtime-retained type annotation targeting classes. It has no members.

## Control Flow
`ReconRestServletModule` scans API packages for `@AdminOnly`, builds resource paths from annotated classes, and applies `ReconAdminFilter` to those paths when security and authorization are enabled.

## State And Persistence
No state or persistence exists.

## Dependencies And Integration Points
It depends on Java annotations and JAX-RS `@Path` by convention. It is used by endpoints such as heatmap, blocks, buckets, and containers.

## Risks
The annotation has effect only if package scanning discovers it and authorization is enabled. Method-level restrictions are not supported. A class missing `@Path` or with unusual path composition can produce incorrect filter paths.

## Test Signals
Tests should assert annotated resources are discovered, admin filters are added for their paths, and unannotated resources remain accessible according to the auth policy.
