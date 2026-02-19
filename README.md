# API Ventas

API REST desarrollada en **FastAPI** para la creación de comprobantes de venta en Oracle.
Inserta registros en `FACTURA_VENTAS` y `DET_FAC_VEN`. La tabla `PENDIENTES` se puebla automáticamente mediante un trigger Oracle existente.

---

## Requisitos

- Python 3.10+
- Oracle Instant Client 23.9 instalado en `C:\oracle\instantclient_23_9`
- Acceso a la red interna (Oracle en `192.168.160.26`)

---

## Instalación

```bash
pip install -r requirements.txt
```

---

## Levantar el servidor

```bash
uvicorn main:app --reload
```

Swagger UI disponible en: `http://localhost:8000/docs`

---

## Entornos

La conexión se configura en `db.py`. Actualmente apunta a **TEST**.

| Entorno | Usuario        | DSN                          |
|---------|----------------|------------------------------|
| TEST    | REDV12_TEST005 | 192.168.160.26:1521/PRODRDL  |
| PROD    | REDV12_EMP005  | 192.168.160.26:1521/PRODRDL  |

Para cambiar a PROD, editar `db.py`:
```python
DB_CONFIG = {
    "user": "REDV12_EMP005",
    "password": "REDV12_EMP005",
    "dsn": "192.168.160.26:1521/PRODRDL",
}
```

### Cliente de prueba en TEST

| Campo       | Valor           |
|-------------|-----------------|
| `C_CLIENTE` | 456             |
| `N_CLIENTE` | VENTA INTERNA   |

Este cliente es un clon del cliente 123 de PROD, creado exclusivamente para pruebas en TEST.

---

## Endpoint

### `POST /comprobante`

Crea un comprobante de venta completo (cabecera + líneas de detalle).

**URL:** `http://localhost:8000/comprobante`
**Method:** `POST`
**Content-Type:** `application/json`

---

### Campos que NO se informan en el payload (la API los gestiona)

| Campo         | Origen                                                          |
|---------------|-----------------------------------------------------------------|
| `ID`          | Secuencia Oracle `SEQ_FACTURAS_VEN.NEXTVAL`                     |
| `R_COMPROBAN` | Tabla `NUMERADORES` (C_NUMERADOR = 20), autoincremental atómico |

### Campos fijos en cabecera (hardcodeados, no se informan)

| Campo             | Valor |
|-------------------|-------|
| `C_COMPROBANTE`   | 21    |
| `C_TIPO_COMPRO`   | 2     |
| `C_SUCURSAL`      | 1     |
| `C_EMPRESA`       | 5     |
| `C_VENDEDOR`      | 0     |
| `M_BASICO_EXENTO` | 0     |

### Campos fijos en detalle (hardcodeados, no se informan)

| Campo          | Valor |
|----------------|-------|
| `C_TIPO_CLASE` | 40    |
| `C_DEPOSITO`   | 79    |
| `M_COSTO`      | 0     |
| `C_NOTA`       | 0     |

---

### Request Body

```json
{
  "observaciones": "20123456781 | Juan Pérez | ORD-00123",
  "cabecera": {
    "c_cliente":     456,
    "f_factura":     "2026-02-13T09:09:00",
    "q_total_de_ar": 2.0,
    "m_basico_grav": 74538.0,
    "m_basic_total": 74538.0,
    "m_descuento":   0.0,
    "descuento":     0.0,
    "m_impuesto":    29442.0,
    "m_total":       103980.0
  },
  "lineas": [
    {
      "c_articulo":     "1302400005",
      "c_tamanio":      "145",
      "c_cuenta":       0,
      "q_articulo":     2.0,
      "m_unit_impreso": 37269.0,
      "m_impuest_neto": 29442.4,
      "m_prec_venta":   74538.0,
      "pc_desc_uno":    0.0,
      "pc_desc_dos":    0.0,
      "m_desc_total":   0.0
    }
  ]
}
```

#### Campo `observaciones`

| Campo           | Tipo   | Requerido | Descripción |
|-----------------|--------|-----------|-------------|
| `observaciones` | string | Sí        | Identificación del comprobante de origen en la plataforma. Se almacena tanto en la cabecera (`FACTURA_VENTAS.OBSERVACIONES`) como en cada línea de detalle (`DET_FAC_VEN.OBSERVACIONES`). |

**Formato esperado:**
```
"RUT | Nombre del cliente | Comprobante plataforma"
```

**Ejemplo:**
```
"20123456781 | Juan Pérez | ORD-00123"
```

> Este campo permite trazabilidad entre el comprobante generado en el ERP y el pedido/orden originado en la plataforma externa.

---

#### Descripción de campos — Cabecera

| Campo           | Tipo     | Requerido   | Descripción                                 |
|-----------------|----------|-------------|---------------------------------------------|
| `c_cliente`     | integer  | Sí          | Código del cliente                          |
| `f_factura`     | datetime | Sí          | Fecha y hora del comprobante (ISO 8601)     |
| `q_total_de_ar` | float    | Sí          | Cantidad total de artículos del comprobante |
| `m_basico_grav` | float    | Sí          | Monto básico gravado (sin IVA)              |
| `m_basic_total` | float    | Sí          | Monto básico total                          |
| `m_descuento`   | float    | No (def. 0) | Monto de descuento en $                     |
| `descuento`     | float    | No (def. 0) | Porcentaje de descuento                     |
| `m_impuesto`    | float    | Sí          | Monto de impuesto (IVA)                     |
| `m_total`       | float    | Sí          | Total del comprobante (gravado + IVA)       |

> **Nota:** Los importes vienen calculados por el sistema llamante. La API los inserta tal cual, sin recalcular.

#### Descripción de campos — Líneas de detalle

Cada elemento del array `lineas` representa un renglón del comprobante.

| Campo            | Tipo    | Requerido   | Descripción                                       |
|------------------|---------|-------------|---------------------------------------------------|
| `c_articulo`     | string  | Sí          | Código del artículo                               |
| `c_tamanio`      | string  | Sí          | Código de tamaño del artículo                     |
| `c_cuenta`       | integer | No (def. 0) | Indicador de línea (0 = primera, 1 = siguientes)  |
| `q_articulo`     | float   | Sí          | Cantidad                                          |
| `m_unit_impreso` | float   | Sí          | Precio unitario impreso (con IVA)                 |
| `m_impuest_neto` | float   | Sí          | Monto de IVA neto de la línea                     |
| `m_prec_venta`   | float   | Sí          | Precio de venta total de la línea                 |
| `pc_desc_uno`    | float   | No (def. 0) | % descuento 1                                     |
| `pc_desc_dos`    | float   | No (def. 0) | % descuento 2                                     |
| `m_desc_total`   | float   | No (def. 0) | Monto total de descuento de la línea              |

---

### Response — 201 Created

```json
{
  "id": 122002,
  "r_comproban": 26020093,
  "lineas_insertadas": 1
}
```

| Campo               | Descripción                                     |
|---------------------|-------------------------------------------------|
| `id`                | ID generado en `FACTURA_VENTAS`                 |
| `r_comproban`       | Número de comprobante generado por el numerador |
| `lineas_insertadas` | Cantidad de líneas insertadas en `DET_FAC_VEN`  |

---

### Respuestas de error

| HTTP | Motivo                                                       |
|------|--------------------------------------------------------------|
| 422  | Payload inválido (faltan campos requeridos) o `lineas` vacío |
| 500  | Error de base de datos (ver `detail` en el body)             |

---

## Estructura del proyecto

```
API_VENTAS/
├── main.py               # App FastAPI, registro de routers
├── db.py                 # Conexión Oracle (thick mode para 11g)
├── models.py             # Schemas Pydantic (request / response)
├── requirements.txt      # Dependencias Python
└── routers/
    └── comprobante.py    # Lógica del endpoint POST /comprobante
```

---

## Tablas Oracle involucradas

| Tabla              | Rol                                                         |
|--------------------|-------------------------------------------------------------|
| `FACTURA_VENTAS`   | Cabecera del comprobante                                    |
| `DET_FAC_VEN`      | Líneas de detalle (FK: `FAC_ID → FACTURA_VENTAS.ID`)        |
| `PENDIENTES`       | Movimientos de stock (poblada por trigger en `DET_FAC_VEN`) |
| `NUMERADORES`      | Tabla de numeración correlativa (`C_NUMERADOR = 20`)        |
| `SEQ_FACTURAS_VEN` | Secuencia Oracle para el ID de `FACTURA_VENTAS`             |
