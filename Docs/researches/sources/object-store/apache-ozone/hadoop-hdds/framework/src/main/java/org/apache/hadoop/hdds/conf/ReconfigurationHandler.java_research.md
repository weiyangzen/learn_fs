# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/ReconfigurationHandler.java

## Purpose

`ReconfigurationHandler` is the HDDS runtime reconfiguration coordinator. It extends Hadoop `ReconfigurableBase` and implements the public `ReconfigureProtocol`, exposing admin RPC methods that reload configuration, report task status, and list allowed properties. It also maps individual property names or whole prefixes to implementation callbacks.

## Important APIs, Types, and Functions

The key registration APIs are `register(String, UnaryOperator<String>)`, `register(ReconfigurableConfig)`, and `registerPrefix(String)`. Runtime RPC APIs are `startReconfigure()`, `getReconfigureStatus()`, `listReconfigureProperties()`, and `getServerName()`. Completion hooks are `registerCompleteCallback`, `setReconfigurationCompleteCallback`, and `defaultLoggingCallback`.

## Control Flow

Construction installs a Hadoop reconfiguration-complete callback. Starting reconfiguration first invokes `requireAdminPrivilege.accept("startReconfiguration")`, then starts the inherited background task. When the task completes, `getNewConf()` creates a fresh `OzoneConfiguration`, changed keys are converted to a `Map<String, Boolean>` where `false` means deletion, and registered callbacks/listeners are invoked.

## State and Persistence Behavior

The handler keeps concurrent maps/sets of explicit and prefix properties. It does not persist state itself; the persisted source is the normal configuration files loaded by `ReconfigurableBase`.

## Dependencies and Integration Points

It integrates with Hadoop `ReconfigurationTaskStatus`, HDDS `ReconfigurableConfig`, `ReconfigurationChangeCallback`, and the PB `ReconfigureProtocol` translators.

## Risks and Test Signals

`completeCallbacks` is an unsynchronized `ArrayList`, so callbacks should be registered during service setup, not while reconfiguration is completing. Prefix registrations use identity behavior unless a concrete property callback exists. Tests should cover admin checks, prefix matching, callback deletion flags, exception wrapping into `ReconfigurationException`, and sorted property listing.
