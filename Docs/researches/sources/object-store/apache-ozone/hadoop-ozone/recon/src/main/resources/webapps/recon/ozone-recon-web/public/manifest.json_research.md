# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/public/manifest.json


Purpose: CRA/PWA manifest metadata for the Recon web bundle, currently generic `React App` / `Create React App Sample` branding with `favicon.ico`, `start_url: "."`, standalone display, black theme color, and white background.

Important APIs/types/functions: Static JSON consumed by browser install/PWA metadata and the build pipeline; no runtime code.

Control flow/state/persistence: None in the file itself. Browser may cache manifest metadata and use it when the app is installed or bookmarked.

Dependencies/integration points: Referenced from the public HTML/build output. It must stay valid JSON and keep icon paths aligned with public assets.

Risks/test signals: Branding is stale for Ozone Recon and could surface in install prompts. No direct tests cover it; validation is build-time JSON parsing and manual browser/PWA inspection.
