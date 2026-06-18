# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/BooleanTriFunction.java

Purpose: `BooleanTriFunction` is a generic three-argument functional interface with a composable return type. Despite its name, it is not constrained to boolean output.

Important APIs/types/functions: `apply(T, U, V)` returns `R`. `andThen(Function<? super R, ? extends K>)` composes a post-processing function and returns a new `BooleanTriFunction<T, U, V, K>`.

Control flow: callers invoke `apply()` directly or through composed functions. `andThen()` null-checks the follow-up function with `Objects.requireNonNull`.

State and persistence: no state beyond captured lambda state in implementations.

Dependencies/integration: depends on `java.util.function.Function`. Used where a tri-argument lambda is needed without introducing a concrete class.

Risks: class name suggests boolean-specific behavior but generic signature permits any `R`, which can confuse readers. No checked exception support.

Test signals: no direct test found for this tiny interface; usage sites provide compile-time coverage.
