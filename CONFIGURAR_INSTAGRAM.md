# Activar el publicador gratuito (sin Metricool)

Se hace una sola vez. Después, GitHub publica los Reels de `publicaciones.json` cada 15 minutos.

## 1. Cuenta de Instagram
@fichalo.app tiene que ser cuenta **profesional** (Empresa o Creador). Instagram → Configuración → Tipo de cuenta.

## 2. App de Meta y token
1. Entra en https://developers.facebook.com → **Mis apps** → **Crear app**.
2. Elige el caso de uso de **Instagram** (gestionar mensajes y contenido en Instagram) y tipo **Empresa**.
3. Dentro de la app: **Instagram → Configuración de la API con inicio de sesión de Instagram**.
4. En **Generar identificadores de acceso**, pulsa **Añadir cuenta**, entra con @fichalo.app y acepta los permisos
   (`instagram_business_basic` e `instagram_business_content_publish`).
5. Copia el **token** que aparece y el **ID de usuario de Instagram** de la cuenta (número).
   La app puede quedarse en modo desarrollo: solo publica en tu propia cuenta.

## 3. Secretos en GitHub
Repo `fichalo-reels` → **Settings → Secrets and variables → Actions**:
- Pestaña **Secrets** → New repository secret:
  - `IG_TOKEN` = el token del paso 2
  - `IG_USER_ID` = el ID de usuario de Instagram
  - `GH_PAT` = (opcional, para renovar el token solo) un token de GitHub *fine-grained* con acceso a este repo y permiso **Secrets: Read and write**. Sin él, el token de Instagram caduca a los 60 días y habrá que repetir el paso 2.
- Pestaña **Variables** → New repository variable: `PUBLICADOR_ACTIVO` = `si`

## 4. Probar
**Actions → Publicar Reels → Run workflow**. Si en el registro sale `Cuenta: fichalo.app ...`, está funcionando.
Si falla, GitHub te manda un email: suele ser el token.
