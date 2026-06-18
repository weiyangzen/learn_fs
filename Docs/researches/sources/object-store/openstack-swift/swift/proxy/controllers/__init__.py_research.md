# sources/object-store/openstack-swift/swift/proxy/controllers/__init__.py

## Purpose
This package initializer provides the public controller import surface for Swift proxy controllers. It imports the base `Controller`, concrete `InfoController`, `ObjectControllerRouter`, `AccountController`, and `ContainerController`, and publishes them through `__all__`.

## Important APIs, Types, and Functions
The file exports `AccountController`, `ContainerController`, `Controller`, `InfoController`, and `ObjectControllerRouter`. It defines no functions or classes itself.

## Control Flow
Importing this module imports each listed controller module. That makes controller classes available from `swift.proxy.controllers` but also means import-time errors in any concrete controller affect package import.

## State and Persistence Behavior
The only state is the module-level `__all__` list. No persistence or runtime mutation is performed.

## Dependencies and Integration Points
It ties together controller implementations used by the proxy server routing layer. It depends on `base.py`, `info.py`, `obj.py`, `account.py`, and `container.py`.

## Risks and Edge Cases
Because it imports `ObjectControllerRouter`, package import may load object-controller dependencies even when a caller only needs account or container controllers. Keep exports synchronized with real controller class names.

## Test Signals
Import-surface tests should verify `from swift.proxy.controllers import ...` works for every `__all__` symbol.
