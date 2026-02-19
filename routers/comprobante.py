from fastapi import APIRouter, HTTPException
from db import get_connection
from models import ComprobanteRequest, ComprobanteResponse

router = APIRouter(prefix="/comprobante", tags=["Comprobante"])

# Campos fijos para C_TIPO_COMPRO=2 / C_COMPROBANTE=21
_CAB_FIJOS = {
    "C_COMPROBANTE": 21,
    "C_TIPO_COMPRO": 2,
    "C_SUCURSAL": 1,
    "C_EMPRESA": 5,
    "C_VENDEDOR": 0,
    "M_BASICO_EXENTO": 0,
}

_DET_FIJOS = {
    "C_TIPO_CLASE": 40,
    "C_DEPOSITO": 79,
    "M_COSTO": 0,
    "C_NOTA": 0,
}

# C_NUMERADOR correspondiente a C_TIPO_COMPRO=2 / C_COMPROBANTE=21
_C_NUMERADOR = 20


@router.post("", response_model=ComprobanteResponse, status_code=201)
def crear_comprobante(payload: ComprobanteRequest):
    if not payload.lineas:
        raise HTTPException(status_code=422, detail="Debe informar al menos una línea.")

    cab = payload.cabecera

    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            # 1. Obtener nuevo ID de cabecera desde secuencia
            cursor.execute("SELECT SEQ_FACTURAS_VEN.NEXTVAL FROM DUAL")
            nuevo_id = cursor.fetchone()[0]

            # 2. Obtener y actualizar numerador (dentro de la misma transacción)
            cursor.execute(
                "SELECT R_ULTIMO FROM NUMERADORES WHERE C_NUMERADOR = :cn FOR UPDATE",
                {"cn": _C_NUMERADOR},
            )
            row = cursor.fetchone()
            if row is None:
                raise HTTPException(status_code=500, detail="Numerador no encontrado.")
            nuevo_r_comproban = row[0] + 1
            cursor.execute(
                "UPDATE NUMERADORES SET R_ULTIMO = :r WHERE C_NUMERADOR = :cn",
                {"r": nuevo_r_comproban, "cn": _C_NUMERADOR},
            )

            # 3. Insert cabecera
            cursor.execute(
                """
                INSERT INTO FACTURA_VENTAS (
                    ID, C_COMPROBANTE, C_TIPO_COMPRO, C_SUCURSAL, C_EMPRESA,
                    C_CLIENTE, C_VENDEDOR, F_FACTURA, R_COMPROBAN,
                    Q_TOTAL_DE_AR, M_BASICO_GRAV, M_BASICO_EXENTO,
                    M_BASIC_TOTAL, M_DESCUENTO, DESCUENTO, M_IMPUESTO, M_TOTAL,
                    OBSERVACIONES
                ) VALUES (
                    :id, :c_comprobante, :c_tipo_compro, :c_sucursal, :c_empresa,
                    :c_cliente, :c_vendedor, :f_factura, :r_comproban,
                    :q_total_de_ar, :m_basico_grav, :m_basico_exento,
                    :m_basic_total, :m_descuento, :descuento, :m_impuesto, :m_total,
                    :observaciones
                )
                """,
                {
                    "id": nuevo_id,
                    **_CAB_FIJOS,
                    "c_cliente": cab.c_cliente,
                    "f_factura": cab.f_factura,
                    "r_comproban": nuevo_r_comproban,
                    "q_total_de_ar": cab.q_total_de_ar,
                    "m_basico_grav": cab.m_basico_grav,
                    "m_basic_total": cab.m_basic_total,
                    "m_descuento": cab.m_descuento,
                    "descuento": cab.descuento,
                    "m_impuesto": cab.m_impuesto,
                    "m_total": cab.m_total,
                    "observaciones": payload.observaciones,
                },
            )

            # 4. Insert líneas
            for nro, linea in enumerate(payload.lineas, start=1):
                cursor.execute(
                    """
                    INSERT INTO DET_FAC_VEN (
                        FAC_ID, ID, C_ARTICULO, C_TAMAÑO, C_TIPO_CLASE,
                        C_DEPOSITO, C_CUENTA, Q_ARTICULO,
                        M_UNIT_IMPRESO, M_IMPUEST_NETO, M_PREC_VENTA,
                        PC_DESC_UNO, PC_DESC_DOS, M_DESC_TOTAL, M_COSTO, C_NOTA,
                        OBSERVACIONES
                    ) VALUES (
                        :fac_id, :id, :c_articulo, :c_tamanio, :c_tipo_clase,
                        :c_deposito, :c_cuenta, :q_articulo,
                        :m_unit_impreso, :m_impuest_neto, :m_prec_venta,
                        :pc_desc_uno, :pc_desc_dos, :m_desc_total, :m_costo, :c_nota,
                        :observaciones
                    )
                    """,
                    {
                        "fac_id": nuevo_id,
                        "id": nro,
                        "c_articulo": linea.c_articulo,
                        "c_tamanio": linea.c_tamanio,
                        **_DET_FIJOS,
                        "c_cuenta": linea.c_cuenta,
                        "q_articulo": linea.q_articulo,
                        "m_unit_impreso": linea.m_unit_impreso,
                        "m_impuest_neto": linea.m_impuest_neto,
                        "m_prec_venta": linea.m_prec_venta,
                        "pc_desc_uno": linea.pc_desc_uno,
                        "pc_desc_dos": linea.pc_desc_dos,
                        "m_desc_total": linea.m_desc_total,
                        "observaciones": payload.observaciones,
                    },
                )

            # 5. Commit — el trigger Oracle puebla PENDIENTES automáticamente
            conn.commit()

        except HTTPException:
            conn.rollback()
            raise
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            cursor.close()

    return ComprobanteResponse(
        id=nuevo_id,
        r_comproban=nuevo_r_comproban,
        lineas_insertadas=len(payload.lineas),
    )
