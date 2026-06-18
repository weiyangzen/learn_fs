# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconGuiceServletContextListener.java

## Purpose
`ReconGuiceServletContextListener` exposes the Recon Guice injector to the servlet container and to internal code that runs outside Jersey request handling.

## Important APIs, Types, And Functions
It extends `GuiceServletContextListener`, overrides `getInjector()`, and provides package-visible `setInjector(Injector)` plus public static `getGlobalInjector()`.

## Control Flow
`ReconServer` creates the injector and calls `setInjector` before starting the HTTP server. Jetty/Guice servlet startup then retrieves the same injector through `getInjector`.

## State And Persistence
State is a static `Injector` reference. No persistence is involved.

## Dependencies And Integration Points
It bridges server startup, Guice servlet integration, and upgrade actions that need injector access outside Jersey. `ReconRestServletModule` separately bridges Guice into Jersey/HK2.

## Risks
Static injector state can leak across tests or restarts in the same JVM. `getInjector()` can return null if servlet startup happens before `ReconServer` sets it.

## Test Signals
Tests should verify setter/getter behavior, servlet listener access, and reset/isolation patterns in embedded server tests.
