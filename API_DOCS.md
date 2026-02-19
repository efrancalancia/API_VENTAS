# API Ventas — Documentación de integración

API REST para la creación de comprobantes de venta. Desarrollada con FastAPI.

> La documentación interactiva completa (Swagger UI) está disponible en `/docs` una vez que el servidor esté corriendo.

---

## Base URL

```
http://<host>:<puerto>
```

---

## Endpoints

### POST `/comprobante`

Crea un comprobante de venta con su cabecera y líneas de detalle.

**Content-Type:** `application/json`
**Response status:** `201 Created`

---

## Estructura del request

```json
{
  "observaciones": "string",
  "cabecera": { ... },
  "lineas": [ { ... } ]
}
```

### Campo raíz

| Campo          | Tipo   | Requerido | Descripción |
|----------------|--------|-----------|-------------|
| `observaciones`| string | Sí        | Texto libre. Formato sugerido: `"RUT \| Nombre cliente \| N° comprobante plataforma"` |
| `cabecera`     | objeto | Sí        | Datos de la cabecera del comprobante |
| `lineas`       | array  | Sí        | Debe contener al menos una línea |

---

### Objeto `cabecera`

| Campo           | Tipo    | Requerido | Default | Descripción |
|-----------------|---------|-----------|---------|-------------|
| `c_cliente`     | integer | Sí        | —       | Código de cliente |
| `f_factura`     | datetime| Sí        | —       | Fecha y hora del comprobante. Formato ISO 8601: `"2025-01-15T10:30:00"` |
| `q_total_de_ar` | float   | Sí        | —       | Cantidad total de artículos |
| `m_basico_grav` | float   | Sí        | —       | Monto básico gravado (neto sin IVA) |
| `m_basic_total` | float   | Sí        | —       | Monto básico total |
| `m_descuento`   | float   | No        | `0.0`   | Monto de descuento aplicado |
| `descuento`     | float   | No        | `0.0`   | Porcentaje de descuento |
| `m_impuesto`    | float   | Sí        | —       | Monto total de impuesto (IVA) |
| `m_total`       | float   | Sí        | —       | Monto total del comprobante |

---

### Objeto `lineas` (cada elemento)

| Campo            | Tipo    | Requerido | Default | Descripción |
|------------------|---------|-----------|---------|-------------|
| `c_articulo`     | string  | Sí        | —       | Código del artículo |
| `c_tamanio`      | string  | Sí        | —       | Código de tamaño del artículo |
| `c_cuenta`       | integer | No        | `0`     | Código de cuenta contable |
| `q_articulo`     | float   | Sí        | —       | Cantidad del artículo |
| `m_unit_impreso` | float   | Sí        | —       | Precio unitario con impuesto (precio de lista impreso) |
| `m_impuest_neto` | float   | Sí        | —       | Monto de impuesto neto de la línea |
| `m_prec_venta`   | float   | Sí        | —       | Precio de venta final de la línea |
| `pc_desc_uno`    | float   | No        | `0.0`   | Porcentaje de descuento 1 |
| `pc_desc_dos`    | float   | No        | `0.0`   | Porcentaje de descuento 2 |
| `m_desc_total`   | float   | No        | `0.0`   | Monto total de descuento de la línea |

---

## Estructura del response

```json
{
  "id": 10045,
  "r_comproban": 3821,
  "lineas_insertadas": 3
}
```

| Campo               | Tipo    | Descripción |
|---------------------|---------|-------------|
| `id`                | integer | ID interno generado para el comprobante |
| `r_comproban`       | integer | Número de comprobante correlativo asignado |
| `lineas_insertadas` | integer | Cantidad de líneas de detalle procesadas |

---

## Ejemplo completo

### Request

```json
POST /comprobante

{
  "observaciones": "20345678-9 | Juan Pérez | ORD-2025-00123",
  "cabecera": {
    "c_cliente": 1042,
    "f_factura": "2025-06-10T14:22:00",
    "q_total_de_ar": 3,
    "m_basico_grav": 2521.01,
    "m_basic_total": 2521.01,
    "m_descuento": 0.0,
    "descuento": 0.0,
    "m_impuesto": 478.99,
    "m_total": 3000.00
  },
  "lineas": [
    {
      "c_articulo": "ART001",
      "c_tamanio": "M",
      "q_articulo": 2,
      "m_unit_impreso": 1000.00,
      "m_impuest_neto": 319.33,
      "m_prec_venta": 2000.00,
      "pc_desc_uno": 0.0,
      "pc_desc_dos": 0.0,
      "m_desc_total": 0.0
    },
    {
      "c_articulo": "ART002",
      "c_tamanio": "U",
      "q_articulo": 1,
      "m_unit_impreso": 1000.00,
      "m_impuest_neto": 159.66,
      "m_prec_venta": 1000.00
    }
  ]
}
```

### Response `201 Created`

```json
{
  "id": 10045,
  "r_comproban": 3821,
  "lineas_insertadas": 2
}
```

---

## Errores

| Código | Descripción |
|--------|-------------|
| `422`  | Datos inválidos o faltantes (incluye el detalle de qué campo falló) |
| `422`  | El array `lineas` está vacío |
| `500`  | Error interno al procesar el comprobante |

### Ejemplo error `422`

```json
{
  "detail": "Debe informar al menos una línea."
}
```

---

## Notas para el desarrollador

- Todos los montos deben enviarse en la misma moneda sin símbolo (valores numéricos).
- El campo `f_factura` acepta formato ISO 8601. Ejemplo: `"2025-06-10T14:22:00"`.
- El campo `observaciones` se replica en cada línea del detalle automáticamente.
- El número de comprobante (`r_comproban`) es asignado por el sistema de forma correlativa; no debe enviarse en el request.
- Un comprobante creado exitosamente dispara procesos internos automáticos en el sistema destino.
