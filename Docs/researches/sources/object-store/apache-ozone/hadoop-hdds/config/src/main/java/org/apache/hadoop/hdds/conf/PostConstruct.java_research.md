# sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/PostConstruct.java

## Purpose
Runtime-retained method annotation for hooks that should run after configuration object injection.

## Important APIs, Types, And Functions
No members. It targets methods and is discovered by `ConfigurationReflectionUtil.callPostConstruct` through public `getMethods()`.

## Control Flow
After full object creation or during single-property reconfiguration, reflection invokes every public method annotated with `@PostConstruct`. Reconfiguration rolls back the changed field if a post-construct hook fails.

## State And Persistence
The annotation itself has no state. Hook methods may mutate object state or external state.

## Dependencies And Integration Points
Integrated with `ConfigurationSource.getObject` and `ConfigurationReflectionUtil.reconfigureProperty`.

## Risks
Only public inherited methods are scanned. Hooks with side effects are not fully rolled back except for the reconfigured field. Checked exceptions are wrapped.

## Test Signals
Tests should cover hook execution after injection, runtime exception propagation, rollback on reconfiguration failure, and behavior for non-public annotated methods.
