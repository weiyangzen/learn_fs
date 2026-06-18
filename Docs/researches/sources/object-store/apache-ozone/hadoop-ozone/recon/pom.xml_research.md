# sources/object-store/apache-ozone/hadoop-ozone/recon/pom.xml

## Purpose
The Recon Maven module POM builds the `ozone-recon` service, wires backend dependencies, runs jOOQ code generation, compiles generated sources, builds the Recon web frontend with pnpm, and packages web assets into the service artifact.

## Important APIs, Types, And Functions
Key build plugins are `maven-compiler-plugin` with `ConfigFileGenerator`, `exec-maven-plugin` running `org.apache.ozone.recon.codegen.JooqCodeGenerator`, `build-helper-maven-plugin` adding generated sources, `spotbugs-maven-plugin`, `frontend-maven-plugin`, `maven-clean-plugin`, and `maven-resources-plugin`. Dependencies span Guice/Jersey/HK2, jOOQ, Derby/SQLite, Spring JDBC/TX, SCM/OM modules, RocksDB, commons libraries, metrics/chatbot libraries, and tests.

## Control Flow
During Maven execution, generated config files are handled by annotation processing, Recon schema codegen runs in `generate-resources`, generated Java sources are added in `generate-sources`, frontend dependencies are installed and built, and built webapp files are copied during `process-resources`.

## State And Persistence
Build outputs land in `target`, generated Java sources under `target/generated-sources/java`, web build artifacts under the frontend `build` tree and classpath `webapps/recon`, and node/pnpm tooling under `target` plus a configured pnpm store.

## Dependencies And Integration Points
The POM ties the runtime classes in this subset to generated DAO classes, SQL schema definitions, HTTP/Jersey serving, OM/SCM clients, Recon tasks, and frontend resources. `findbugsExcludeFile.xml` is consumed here.

## Risks
The build has several generated-artifact phases; phase ordering matters for compiling DAO consumers. Frontend builds require pnpm lock consistency and network/cache availability. The `ozone-cli-admin` dependency excludes all transitives, so callers must rely on already declared dependencies.

## Test Signals
Signals include successful `generate-resources`, generated DAO compilation, SpotBugs filtering, frontend build/resource copy success, and module tests resolving both compile and runtime dependencies.
