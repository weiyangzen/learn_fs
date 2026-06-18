# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconRestServletModule.java

## Purpose
`ReconRestServletModule` configures Jersey REST serving for Recon APIs, scans resource packages, and installs authentication and admin filters for secured deployments.

## Important APIs, Types, And Functions
Constants define `/api/v1`, the Recon API package, and chatbot API package. `configureServlets()` chooses packages based on chatbot enablement. `configureApi` registers `ServletContainer`, provider package params, and admin endpoint discovery. `addFilters` applies `ReconAuthFilter` and `ReconAdminFilter`. Nested `GuiceResourceConfig` bridges Guice into Jersey HK2.

## Control Flow
At injector setup, the module scans packages with Reflections, detects classes annotated `@AdminOnly`, serves `/api/v1/*`, and conditionally wires filters based on HTTP security and authorization settings. Jersey startup initializes the HK2 bridge using the servlet-context Guice injector.

## State And Persistence
No persistent state exists. Runtime state is servlet/filter configuration and discovered endpoint path sets.

## Dependencies And Integration Points
It integrates Guice Servlet, Jersey, HK2 bridge, Ozone HTTP security utilities, `AdminOnly`, `ReconAuthFilter`, `ReconAdminFilter`, and optional chatbot endpoints.

## Risks
Reflections scanning must find annotation metadata correctly; path construction from resource classes controls admin filtering. If authorization is disabled, admin-only resources still skip `ReconAdminFilter`. Missing packages only log warnings, so requests fail later.

## Test Signals
Tests should verify servlet mapping, provider package list, chatbot conditional registration, admin filter path generation, auth filter enablement, and Guice-to-HK2 injection of endpoint resources.
