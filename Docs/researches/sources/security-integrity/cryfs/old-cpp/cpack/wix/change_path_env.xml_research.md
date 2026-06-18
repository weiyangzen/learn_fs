# sources/security-integrity/cryfs/old-cpp/cpack/wix/change_path_env.xml

Purpose: WiX CPack patch fragment that adds the installed CryFS `bin` directory to the system `PATH` on Windows.

Important APIs and types: Defines a `CPackWiXPatch` with `CPackWiXFragment Id="CM_CP_bin.cryfs.exe"` and an `Environment` element `Id="MyPath"` with `Action="set"`, `Part="first"`, `Name="PATH"`, `Value="[INSTALL_ROOT]bin"`, and `System="yes"`.

Control flow: CPack consumes this XML patch during WiX generation when `CPACK_WIX_PATCH_FILE` points to it. There is no standalone execution.

State and persistence behavior: The resulting MSI mutates the machine-wide Windows PATH by prepending the install bin path.

Dependencies and integration points: Referenced from `cpack/CMakeLists.txt` for Windows packaging.

Risks: System PATH mutation is global and can have ordering/collision effects. The fragment ID must match CPack's generated component ID; if CPack changes component naming, the patch stops applying.

Test signals: Installed MSI should expose `cryfs.exe` on PATH and WiX generation should succeed without missing-fragment errors.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/cpack/wix/change_path_env.xml` completely for this pass (7 lines, 215 bytes).
