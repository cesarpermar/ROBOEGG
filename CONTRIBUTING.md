# Contributing to ROBOEGG

¡Gracias por tu interés en contribuir a ROBOEGG! Este documento describe las convenciones y procesos para colaborar en el proyecto.

## 📋 Tabla de Contenidos

- [Código de Conducta](#código-de-conducta)
- [¿Cómo Contribuir?](#cómo-contribuir)
- [Convención de Commits](#convención-de-commits)
- [Estructura de Branches](#estructura-de-branches)
- [Estilo de Código](#estilo-de-código)

## Código de Conducta

Este proyecto se adhiere al [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). Al participar, se espera que cumplas con este código.

## ¿Cómo Contribuir?

1. **Fork** el repositorio
2. Crea una branch desde `main`: `git checkout -b feat/mi-feature`
3. Haz tus cambios siguiendo las convenciones de código
4. Confirma que los imports funcionan: `python -c "from src.scara_control import config"`
5. Haz commit usando la convención de commits
6. Abre un Pull Request

## Convención de Commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

```
tipo(alcance): descripción breve

[cuerpo opcional]
```

### Tipos permitidos:

| Tipo | Descripción |
|------|-------------|
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de error |
| `docs` | Solo cambios en documentación |
| `refactor` | Refactorización sin cambio funcional |
| `test` | Agregar o corregir tests |
| `chore` | Tareas de mantenimiento |
| `safety` | Cambios relacionados con seguridad del robot |
| `cal` | Cambios en el sistema de calibración |

### Ejemplos:

```
feat(kinematics): add gamma correction to inverse kinematics
fix(hal): handle serial timeout gracefully  
docs(readme): add D-H parameter table
safety(estop): reduce emergency stop response time
cal(profile): add rotation offset to calibration JSON
```

## Estructura de Branches

| Branch | Propósito |
|--------|-----------|
| `main` | Código estable y funcional |
| `develop` | Integración de features en desarrollo |
| `feat/*` | Features nuevas |
| `fix/*` | Correcciones de bugs |
| `docs/*` | Actualizaciones de documentación |

## Estilo de Código

### Python
- **Docstrings**: Todas las funciones y clases deben tener docstrings
- **Type hints**: Usar type hints en parámetros y retornos
- **Constantes**: `UPPER_SNAKE_CASE`
- **Funciones/variables**: `lower_snake_case`
- **Clases**: `PascalCase`
- **Línea máxima**: 100 caracteres

### Arduino C++
- **Constantes**: `UPPER_SNAKE_CASE` con `const` o `#define`
- **Funciones**: `camelCase`
- **Comentarios**: En español o inglés, pero consistente por archivo

## ⚠️ Reglas de Seguridad para Hardware

> **CRÍTICO**: Cualquier cambio que afecte el movimiento del robot debe:
> 1. Ser probado primero sin conexión al hardware (dry run)
> 2. Incluir validación de zona segura
> 3. Mantener el mecanismo de E-STOP funcional
> 4. Ser revisado por al menos un miembro del equipo
