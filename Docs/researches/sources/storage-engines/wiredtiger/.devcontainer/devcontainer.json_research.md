# sources/storage-engines/wiredtiger/.devcontainer/devcontainer.json

## Purpose
This VS Code devcontainer descriptor names the WiredTiger development container and points the container build at the local Dockerfile.

## Important APIs, Types, and Functions
It configures `"build": {"dockerfile": "Dockerfile"}` and VS Code customizations: clangd, Python, CMake Tools, C/C++, and YAML extensions. Settings disable the Microsoft C/C++ IntelliSense engine and select `clangd`.

## Control Flow, State, and Dependencies
The file is declarative; the devcontainer runtime builds the Dockerfile and applies editor extensions/settings. It depends on VS Code Remote Containers and the Dockerfile in the same directory.

## Integration Points, Risks, and Test Signals
It integrates editor tooling with the repository's CMake compile database and clangd workflow. Risk is extension/settings drift. Signal is a devcontainer opening successfully with clangd and CMake tooling available.
