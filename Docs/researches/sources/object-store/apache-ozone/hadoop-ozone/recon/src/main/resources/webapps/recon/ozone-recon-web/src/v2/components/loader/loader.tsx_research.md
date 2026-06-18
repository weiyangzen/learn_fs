# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/loader/loader.tsx


Purpose: Full-area loading spinner for V2 route Suspense and loading states.

Important APIs/types/functions: Default `Loader`, `loaderStyle`, AntD `Spin`, and `LoadingOutlined`.

Control flow/state/persistence: Stateless render of centered green spinner with large icon.

Dependencies/integration points: Used as `Suspense` fallback in `app.tsx` and potentially elsewhere.

Risks/test signals: No accessible label/text. Inline `paddingTop: '25%'` may not center in all layouts, especially Assistant’s special flex layout.
