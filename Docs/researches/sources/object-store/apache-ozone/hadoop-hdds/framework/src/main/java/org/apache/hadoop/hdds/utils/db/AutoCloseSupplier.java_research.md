# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/AutoCloseSupplier.java

## Purpose
`AutoCloseSupplier<RAW>` is a package-private functional interface combining `Supplier<RAW>` and `AutoCloseable`. It lets code pass suppliers that may own resources while defaulting to no-op cleanup.

## Important APIs and Types
The interface extends `AutoCloseable` and `Supplier<RAW>` and overrides `close()` with a default no-op implementation. Because it is annotated as a functional interface, the abstract method remains `Supplier.get()`.

## Control Flow and State
There is no state or control flow. Implementations can be lambdas for simple suppliers or classes overriding `close` when cleanup is needed.

## Persistence, Dependencies, and Integration
No persistence exists. The only dependency is `java.util.function.Supplier`. It is scoped to the DB package and can be used around codec/raw-value APIs where optional resource cleanup is useful.

## Risks and Test Signals
The no-op default can hide forgotten cleanup if implementers assume close is mandatory. Tests are only needed where concrete implementations allocate resources; they should verify both `get` behavior and idempotent close behavior.
