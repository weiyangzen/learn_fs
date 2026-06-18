# sources/sync-backup/git-crypt/.github/workflows/release-windows.yml

Purpose: GitHub Actions workflow that builds and uploads a Windows x86_64 `git-crypt.exe` release binary when a release is published.

Important APIs/types/functions: build job on `windows-2022`, `msys2/setup-msys2@v2`, package list for MINGW64 toolchain and OpenSSL, `make LDFLAGS="-static-libstdc++ -static -lcrypto -lws2_32 -lcrypt32"`, artifact upload/download, and GitHub Script release asset upload.

Control flow: checkout, install MSYS2/MINGW dependencies, run a static-ish Windows build under the MSYS2 shell, upload `git-crypt.exe`, then upload the downloaded executable to the release as `git-crypt-${release.name}-x86_64.exe`.

State/persistence behavior: the executable is passed through the artifact store and persisted to the release. No signing or checksum state is produced in this workflow.

Dependencies/integration: integrates MSYS2 packages, MinGW OpenSSL, Windows system libraries `ws2_32` and `crypt32`, and the common git-crypt Makefile.

Risks/test signals: static linking flags and OpenSSL/MSYS2 package changes are likely failure points. There is no smoke test after build. Useful signals include `git-crypt.exe --version`, dependency inspection, artifact download validation, and release upload collision handling.
