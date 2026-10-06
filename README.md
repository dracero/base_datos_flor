# Sistema de Consulta de Planificaciones y Bibliografía (FIUBA)

Aplicación Fullstack desarrollada con **Astro (SSR)** y **PostgreSQL 16** para la consulta, exploración y auditoría de planificaciones cuatrimestrales y bibliografía por materia a partir de los datos académicos normalizados.

---

## 🚀 Inicio Rápido con un solo comando

Para levantar **todo el sistema** (base de datos PostgreSQL en Docker + servidor frontend de Astro):

```bash
npm run dev
```

> **Nota:** El comando ejecuta un hook `predev` (`start-db.sh`) que verifica automáticamente el estado del contenedor de PostgreSQL. Si está detenido o no existe, lo levanta y asegura que esté listo para aceptar consultas antes de iniciar Astro.

La aplicación web estará disponible en: **http://localhost:4321**

---

## 🏗️ Arquitectura y Tecnologías

### 1. Base de Datos (PostgreSQL 16 en Docker)
* **Contenedor:** `pg-material-estudio` (puerto `5432`)
* **Base de datos:** `material_estudio`
* **Persistencia:** Volumen Docker `pgdata_material_estudio`
* **Normalización (3FN):**
  * `departamentos`: Matemática, Física, Química.
  * `periodos`: Cuatrimestres registrados (`2023 1C` a `2026 1C`).
  * `docentes`: Docentes responsables con email `@fi.uba.ar`.
  * `asignaturas`: Códigos oficiales y nombres de materias.
  * `agrupamientos`: Comisiones unificadas (`AGPLA0001`, `AGPLA0002`, etc.).
  * `agrupamiento_asignaturas`: Relación N:M entre comisiones y planes.
  * `planificaciones_periodo`: Estado cuatrimestral, links a Drive, completitud.
  * `materiales_estudio`: Libros, apuntes, guías, videos, aulas virtuales y exámenes.

### 2. Frontend (Astro 5 con SSR)
* **Framework:** Astro con adaptador `@astrojs/node` en modo servidor (SSR).
* **Driver DB:** `pg` (Pool de conexiones nativo a PostgreSQL con queries parametrizadas).
* **Estilos:** Vanilla CSS moderno con diseño oscuro tipo dashboard universitario, microinteracciones y badges semánticos.

---

## 📱 Vistas de la Aplicación

1. **Buscador General (`/`)**:
   * Dashboard con 4 métricas clave en vivo (materiales, materias, docentes, cuatrimestres).
   * Buscador por texto libre (título, autor, ISBN, tema, código).
   * Filtros combinables por Departamento, Cuatrimestre y Tipo de Material.
   * Tarjetas interactivas con links directos al Campus Virtual y carpetas en Drive.

2. **Catálogo de Asignaturas (`/materias`)**:
   * Agrupado por departamento académico.
   * Cantidad de recursos y cuatrimestres activos por cada materia.
   * Acceso a la ficha detallada de cada asignatura.

3. **Ficha de Asignatura (`/materias/[codigo]`)**:
   * Historial de planificaciones por cuatrimestre con docente a cargo y estado.
   * Toda la bibliografía de la materia organizada y clasificada.

4. **Planificaciones Cuatrimestrales (`/planificaciones`)**:
   * Auditoría de entregas por cuatrimestre.
   * Porcentaje de cumplimiento (% completas vs pendientes).
   * Acceso directo a los formularios y archivos en Drive.

5. **API REST (`/api/search`)**:
   * Endpoint JSON (`GET /api/search?q=...&depto=...&periodo=...&tipo=...`) para consultas programáticas.

---

## 🛠️ Comandos de Utilidad

```bash
# Iniciar todo (BD + Astro)
npm run dev

# Compilar para producción
npm run build

# Consultar PostgreSQL directamente desde la terminal
./query.sh "SELECT tipo_material, count(*) FROM materiales_estudio GROUP BY tipo_material;"

# Entrar a la consola psql interactiva
./query.sh
```
